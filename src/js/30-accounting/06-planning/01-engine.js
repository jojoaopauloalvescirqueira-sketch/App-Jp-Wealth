// Planejamento patrimonial: nominal USD simulation, independent of Forex policy.
// Source: approved 2026-10-20-planning-reference decision. No DOM, storage or S.
(function (root) {
  'use strict';
  const own = (o, k) => Object.prototype.hasOwnProperty.call(o, k);
  const object = v => v !== null && typeof v === 'object' && !Array.isArray(v);
  const finite = v => typeof v === 'number' && Number.isFinite(v);
  const cents = v => finite(v) && Number.isSafeInteger(Math.round(v * 100)) && Math.abs(v * 100 - Math.round(v * 100)) <= 1e-6;
  const nonnegative = v => cents(v) && v >= 0;
  // Native form and future blue cells use step=any. Actual cash ledgers keep
  // their independent two-decimal validation.
  const premiseAmount = v => finite(v) && v >= 0 && Math.abs(v) <= Number.MAX_SAFE_INTEGER / 100;
  const secretKey = key => /password|passwd|senha|secret|token|credential|authorization|api[-_]?key|private[-_]?key/i.test(key);
  const revision = v => Number.isSafeInteger(v) && v >= 0;
  const clone = v => JSON.parse(JSON.stringify(v));
  const startMonthRange = Object.freeze({ min: '1900-01', max: '2199-12' });
  const profiles = Object.freeze([
    ['high-risk', 'High Risk', .06, .40], ['base', 'Base', .03, .20],
    ['conservative', 'Conservador', .02, .13], ['safety', 'Segurança', .015, .10]
  ].map(p => Object.freeze({ id: p[0], name: p[1], rate: p[2], mdd: p[3], annualRate: (1 + p[2]) ** 12 - 1 })));
  const profile = id => profiles.find(p => p.id === id);
  function correctedZero(flow) {
    const seen = new Set();
    while (object(flow) && !seen.has(flow)) {
      seen.add(flow);
      if (flow.usd !== 0 || !revision(flow.revision) || flow.revision < 2 || !object(flow.previous)
        || flow.previous.id !== flow.id || !revision(flow.previous.revision) || flow.previous.revision >= flow.revision || !nonnegative(flow.previous.usd)) return false;
      if (flow.previous.usd > 0) return true;
      flow = flow.previous;
    }
    return false;
  }
  const validFlowUsd = flow => object(flow) && nonnegative(flow.usd) && (flow.usd > 0 || correctedZero(flow));

  function monthKey(value) {
    if (Object.prototype.toString.call(value) === '[object Date]') {
      if (!Number.isFinite(value.getTime())) return '';
      value = value.toISOString().slice(0, 7);
    }
    return typeof value === 'string' && /^\d{4}-(0[1-9]|1[0-2])$/.test(value) ? value : '';
  }
  function ordinal(month) { return Number(month.slice(0, 4)) * 12 + Number(month.slice(5)) - 1; }
  function addMonths(month, n) {
    if (!monthKey(month) || !Number.isSafeInteger(n)) throw new TypeError('Mês ou deslocamento inválido.');
    const x = ordinal(month) + n;
    if (x < 0 || x > 119999) throw new RangeError('Calendário fora do limite.');
    return String(Math.floor(x / 12)).padStart(4, '0') + '-' + String(x % 12 + 1).padStart(2, '0');
  }
  function quoteRate(q) { return object(q) && finite(q.rate) && q.rate > 0 ? q.rate : null; }
  function validQuote(q) {
    return quoteRate(q) !== null && typeof q.referenceDate === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(q.referenceDate)
      && Number.isFinite(Date.parse(q.referenceDate)) && new Date(q.referenceDate).toISOString().slice(0, 10) === q.referenceDate
      && ((typeof q.fetchedAt === 'string' && Number.isFinite(Date.parse(q.fetchedAt))) || (finite(q.fetchedAt) && q.fetchedAt > 0))
      && typeof q.source === 'string' && !!q.source.trim();
  }
  function normalizeGoal(raw, required) {
    if (raw === undefined || raw === null) {
      if (required) throw new TypeError('A renda ideal é obrigatória.');
      return null;
    }
    if (!object(raw) || !premiseAmount(raw.value) || raw.value <= 0 || !['USD', 'BRL'].includes(raw.currency)) throw new TypeError('Meta monetária inválida.');
    if (raw.currency === 'BRL' && !validQuote(raw.quote)) throw new TypeError('A meta em reais exige cotação com origem e data.');
    const usd = Math.round(raw.value / (raw.currency === 'BRL' ? raw.quote.rate : 1) * 100) / 100;
    if (!finite(usd) || usd <= 0) throw new TypeError('A meta convertida deve ser ao menos US$ 0,01.');
    return Object.assign({}, clone(raw), { usd, quote: raw.currency === 'BRL' ? clone(raw.quote) : null });
  }
  function configErrors(c) {
    const errors = [];
    if (!object(c)) return ['Configuração inválida.'];
    if (typeof c.startMonth !== 'string' || !monthKey(c.startMonth) || c.startMonth < startMonthRange.min || c.startMonth > startMonthRange.max) errors.push('Mês inicial inválido: escolha entre janeiro de1900 e dezembro de2199.');
    if (!premiseAmount(c.initialUsd)) errors.push('Capital inicial inválido.');
    if (!profile(c.profileId)) errors.push('Perfil hipotético inválido.');
    if (!premiseAmount(c.monthlyContributionUsd)) errors.push('Aporte mensal inválido.');
    for (const key of ['adequate', 'ideal']) {
      try { normalizeGoal(c.goals && c.goals[key], key === 'ideal'); } catch (e) { errors.push(key + ': ' + e.message); }
    }
    return errors;
  }
  function createPlan(config, options) {
    options = options || {};
    const errors = configErrors(config);
    if (typeof options.id !== 'string' || !options.id.trim()) errors.push('Identidade do plano inválida.');
    if (typeof options.now !== 'string' || !Number.isFinite(Date.parse(options.now))) errors.push('Data de criação inválida.');
    if (errors.length) throw new TypeError(errors.join(' '));
    const initial = { startMonth: config.startMonth, initialUsd: config.initialUsd, profileId: config.profileId,
      monthlyContributionUsd: config.monthlyContributionUsd,
      goals: { adequate: normalizeGoal(config.goals && config.goals.adequate, false), ideal: normalizeGoal(config.goals.ideal, true) } };
    const plan = Object.assign({ id: options.id, revision: 0 }, initial,
      { future: {}, results: {}, contributions: [], withdrawals: [], closures: {}, history: [], stopAfter: null });
    const rows = timeline(plan, { month: initial.startMonth, reference: true });
    plan.reference = { id: options.id + ':reference', planId: options.id, version: 1, createdAt: options.now, config: clone(initial), rows: clone(rows) };
    return plan;
  }

  // Validating never normalizes, strips unknown fields, repairs or mutates input.
  function validateEnvelope(value) {
    if (value === undefined) return [];
    const errors = [];
    if (!object(value)) return ['Envelope inválido.'];
    const seen = new Set(), pending = [{ value, path: 'planning', leave: false }];
    while (pending.length) {
      const item = pending.pop(), v = item.value;
      if (item.leave) { seen.delete(v); continue; }
      if (v === null || typeof v === 'string' || typeof v === 'boolean' || finite(v)) continue;
      if (!v || typeof v !== 'object' || seen.has(v) || !['[object Object]', '[object Array]'].includes(Object.prototype.toString.call(v))) { errors.push(item.path + ': valor não serializável.'); continue; }
      seen.add(v); pending.push({ value: v, leave: true });
      Object.keys(v).forEach(k => {
        if (secretKey(k)) errors.push(item.path + '.' + k + ': segredo não permitido.');
        pending.push({ value: v[k], path: item.path + '.' + k, leave: false });
      });
    }
    if (value.schemaVersion !== 1) errors.push('Versão do planejamento não suportada.');
    if (!revision(value.revision)) errors.push('Revisão inválida.');
    ['accounts', 'archive', 'audit', 'operations'].forEach(k => { if (!Array.isArray(value[k])) errors.push(k + ': lista obrigatória.'); });
    if(value.pendingConfiguration!==undefined){
      const p=value.pendingConfiguration;
      if(!object(p)||p.scope!=='TODAS'||typeof p.accountId!=='string'||!p.accountId||!Number.isFinite(Date.parse(p.at))||
        !Array.isArray(value.accounts)||!value.accounts.some(a=>a&&a.id===p.accountId&&a.active===false)||value.accounts.some(a=>a&&a.active===true))errors.push('Configuração pendente inválida.');
    }
    const ids = new Set(), plans = new Set();
    (Array.isArray(value.accounts) ? value.accounts : []).forEach((a, i) => {
      const prefix = 'accounts[' + i + ']';
      if (!object(a)) { errors.push(prefix + ': conta inválida.'); return; }
      if (typeof a.id !== 'string' || !a.id.trim() || ids.has(a.id)) errors.push(prefix + ': identidade inválida ou duplicada.');
      ids.add(a.id);
      if (typeof a.name !== 'string' || !a.name.trim()) errors.push(prefix + ': nome obrigatório.');
      ['broker', 'login', 'server'].forEach(k => { if (a[k] !== undefined && typeof a[k] !== 'string') errors.push(prefix + '.' + k + ': texto inválido.'); });
      if (typeof a.active !== 'boolean') errors.push(prefix + ': estado ativo inválido.');
      const p = a.plan;
      if (!object(p)) { errors.push(prefix + ': plano obrigatório.'); return; }
      if (typeof p.id !== 'string' || !p.id.trim() || plans.has(p.id)) errors.push(prefix + ': identidade de plano inválida ou duplicada.');
      plans.add(p.id);
      if (!revision(p.revision)) errors.push(prefix + ': revisão do plano inválida.');
      errors.push(...configErrors(p).map(e => prefix + ': ' + e));
      ['adequate', 'ideal'].forEach(k => {
        const goal = p.goals && p.goals[k];
        if (goal) {
          try { if (!finite(goal.usd) || goal.usd !== normalizeGoal(goal, k === 'ideal').usd) errors.push(prefix + ': conversão da meta inválida.'); }
          catch (_error) { /* configErrors reports the invalid goal. */ }
        }
      });
      if(p.incomeBaselineGoals!==undefined){
        if(!object(p.incomeBaselineGoals))errors.push(prefix+': referência de renda inválida.');
        else for(const k of ['adequate','ideal'])try{const g=p.incomeBaselineGoals[k];if(g!==null&&(!object(g)||normalizeGoal(g,k==='ideal').usd!==g.usd))errors.push(prefix+': referência de renda inválida.');}catch(_error){errors.push(prefix+': referência de renda inválida.');}
      }
      if (!Array.isArray(p.history)) errors.push(prefix + ': histórico inválido.');
      const inRange = m => !!monthKey(m) && !!monthKey(p.startMonth) && ordinal(m) >= ordinal(p.startMonth) && ordinal(m) < ordinal(p.startMonth) + 120;
      ['future', 'results', 'closures'].forEach(k => {
        if (!object(p[k])) { errors.push(prefix + '.' + k + ': mapa obrigatório.'); return; }
        Object.keys(p[k]).forEach(m => {
          const entry = p[k][m];
          if (!inRange(m) || !object(entry)) { errors.push(prefix + '.' + k + '.' + m + ': lançamento inválido.'); return; }
          if (k === 'future') {
            if (own(entry, 'rate') && entry.rate !== '' && entry.rate !== null && (!finite(entry.rate) || entry.rate < -1)) errors.push(prefix + ': taxa futura inválida.');
            if (own(entry, 'contributionUsd') && entry.contributionUsd!=='' && !premiseAmount(entry.contributionUsd)) errors.push(prefix + ': aporte futuro inválido.');
          } else if (k === 'results') {
            if (!cents(entry.usd) || !revision(entry.revision)) errors.push(prefix + ': resultado inválido.');
          } else if (typeof entry.confirmed !== 'boolean' || typeof entry.confirmFlows !== 'boolean' || !revision(entry.revision)
            || (entry.fxQuote !== undefined && entry.fxQuote !== null && !validQuote(entry.fxQuote))) errors.push(prefix + ': fechamento inválido.');
        });
      });
      ['contributions', 'withdrawals'].forEach(k => {
        if (!Array.isArray(p[k])) { errors.push(prefix + '.' + k + ': ledger obrigatório.'); return; }
        const flowIds = new Set();
        p[k].forEach(flow => {
          if (!object(flow) || typeof flow.id !== 'string' || !flow.id || flowIds.has(flow.id) || !inRange(flow.month)
            || !validFlowUsd(flow) || !revision(flow.revision)
            || (flow.brl !== undefined && flow.brl !== null && (!nonnegative(flow.brl) || (flow.brl === 0 && flow.usd !== 0)))) errors.push(prefix + '.' + k + ': fluxo inválido.');
          if (object(flow)) flowIds.add(flow.id);
        });
      });
      if (p.stopAfter !== undefined && p.stopAfter !== null && (!monthKey(p.stopAfter) || !monthKey(p.startMonth)
        || ordinal(p.stopAfter) < ordinal(p.startMonth) - 1 || ordinal(p.stopAfter) > ordinal(p.startMonth) + 119)) errors.push(prefix + ': parada inválida.');
      const ref = p.reference;
      if (!object(ref) || ref.planId !== p.id || ref.version !== 1 || typeof ref.id !== 'string' || !ref.id
        || typeof ref.createdAt !== 'string' || !Number.isFinite(Date.parse(ref.createdAt)) || configErrors(ref.config).length
        || !Array.isArray(ref.rows) || ref.rows.length !== 120) errors.push(prefix + ': referência inicial inválida.');
      else {
        const expected = timeline(Object.assign({}, ref.config, { future: {}, results: {}, contributions: [], withdrawals: [], closures: {} }), { reference: true, month: ref.config.startMonth });
        ref.rows.forEach((r, index) => {
          if (!object(r) || r.month !== addMonths(ref.config.startMonth, index)
            || !['openUsd', 'rate', 'resultUsd', 'contributionUsd', 'withdrawalUsd', 'closeUsd'].every(k => finite(r[k]) && r[k] === expected[index][k])
            || r.openUsd < 0 || r.closeUsd < 0) errors.push(prefix + ': trajetória da referência inválida.');
        });
      }
      if (monthKey(p.startMonth) && ordinal(p.startMonth) + 119 <= 119999 && object(p.closures)) {
        const verification = timeline(p, { month: addMonths(p.startMonth, 119) });
        verification.forEach(r => {
          if (p.closures[r.month] && p.closures[r.month].confirmed === true && !r.finalized) errors.push(prefix + ': fechamento confirmado inválido em ' + r.month + '.');
        });
      }
    });
    if (Array.isArray(value.archive)) value.archive.forEach((entry, i) => {
      const prefix = 'archive[' + i + ']';
      if (!object(entry) || typeof entry.id !== 'string' || !entry.id || typeof entry.accountId !== 'string' || !entry.accountId
        || entry.reason !== 'restartPlan' || typeof entry.archivedAt !== 'string' || !Number.isFinite(Date.parse(entry.archivedAt))
        || !object(entry.account) || !object(entry.plan)) { errors.push(prefix + ': arquivo inválido.'); return; }
      const archived = Object.assign({}, entry.account, { plan: entry.plan });
      errors.push(...validateEnvelope({ schemaVersion: 1, revision: 0, accounts: [archived], archive: [], audit: [], operations: [] }).map(e => prefix + ': ' + e));
    });
    if (Array.isArray(value.operations)) {
      const operationIds = new Set();
      value.operations.forEach((op, index) => {
        const r = object(op) && op.result, b = object(op) && op.base;
        if (!object(op) || typeof op.id !== 'string' || !op.id || operationIds.has(op.id) || typeof op.type !== 'string' || !op.type
          || typeof op.accountId !== 'string' || !op.accountId || typeof op.planId !== 'string' || !op.planId
          || typeof op.at !== 'string' || !Number.isFinite(Date.parse(op.at)) || typeof op.signature !== 'string' || !op.signature
          || !object(b) || !revision(b.revision) || (b.planRevision !== null && !revision(b.planRevision))
          || !object(r) || r.ok !== true || r.status !== 'CONFIRMED' || !Array.isArray(r.errors) || r.errors.length
          || r.operationId !== op.id || r.accountId !== op.accountId || r.planId !== op.planId || !revision(r.revision)) errors.push('operations[' + index + ']: recibo inválido.');
        if (object(op)) operationIds.add(op.id);
      });
    }
    return errors;
  }

  function timeline(plan, options) {
    options = options || {};
    if (own(options, 'month') && !monthKey(options.month)) throw new TypeError('Mês de referência inválido.');
    if (!object(plan) || !monthKey(plan.startMonth)) return [];
    const today = monthKey(options.month) || plan.startMonth;
    const defaultRate = profile(plan.profileId) ? profile(plan.profileId).rate : null;
    const rows = [];
    let open = premiseAmount(plan.initialUsd) ? plan.initialUsd : null, continuous = true;
    function flows(list, month, label, issues) {
      if (!Array.isArray(list)) { issues.push(label + ' inválidos.'); return null; }
      let total = 0;
      for (const f of list) if (object(f) && f.month === month) {
        if (!validFlowUsd(f)) { issues.push(label + ' inválidos.'); return null; }
        total += f.usd;
      }
      if (!finite(total)) { issues.push(label + ' fora do limite.'); return null; }
      return total;
    }
    for (let i = 0; i < 120; i++) {
      const month = addMonths(plan.startMonth, i), issues = [];
      const future = object(plan.future) && own(plan.future, month) ? plan.future[month] : {};
      const result = object(plan.results) && own(plan.results, month) ? plan.results[month] : null;
      const closure = object(plan.closures) && own(plan.closures, month) ? plan.closures[month] : null;
      const hasResult = result !== null;
      const requestedClose = !!closure && closure.confirmed === true;
      const ledgerContribution = options.reference ? 0 : flows(plan.contributions, month, 'Aportes', issues);
      const withdrawal = options.reference ? 0 : flows(plan.withdrawals, month, 'Saques', issues);
      const explicitContribution = object(future) && own(future, 'contributionUsd');
      let planned = explicitContribution ? future.contributionUsd : plan.monthlyContributionUsd;
      const contributionBlank=explicitContribution&&planned==='';
      if(contributionBlank)planned=0;
      // An explicit future edit is the cell's current value. The stop marker
      // supplies a default only; applying a stop writes future zero overrides.
      if (!options.reference && !explicitContribution && plan.stopAfter && month > plan.stopAfter) planned = 0;
      if (!(options.simulation ? finite(planned) && planned >= 0 : premiseAmount(planned))) { issues.push('Aporte previsto inválido.'); planned = null; }
      let rate = object(future) && own(future, 'rate') ? future.rate : defaultRate;
      const explicitRate = object(future) && own(future, 'rate');
      const provisional = !hasResult && explicitRate && (rate === '' || rate === null || rate === undefined);
      if (provisional) rate = 0;
      let resultUsd = null;
      if (hasResult) {
        if (!object(result) || !cents(result.usd)) { issues.push('Resultado em USD inválido.'); rate = null; }
        else if (open === 0 && result.usd !== 0) { issues.push('Resultado não nulo sem capital de abertura.'); rate = null; }
        else { resultUsd = result.usd; rate = open === null ? null : open === 0 ? 0 : resultUsd / open; }
      } else if (!finite(rate) || rate < -1) { issues.push('Taxa mensal inválida.'); rate = null; }
      else if (open !== null) resultUsd = open * rate;
      const hasContributionRecords = !options.reference && Array.isArray(plan.contributions) && plan.contributions.some(f => object(f) && f.month === month);
      // Original Formulario1288–1291 expires a forecast only after month end;
      // recording actual flows replaces its cell with the ledger sum1266–1272.
      // A closure always uses effective records, even when that sum is zero.
      const usePlanned = options.reference || (month >= today && !requestedClose && !hasContributionRecords);
      const contribution = ledgerContribution === null || (usePlanned && planned === null) ? null : usePlanned ? planned : ledgerContribution;
      if (open === null) issues.push('Saldo anterior indisponível.');
      let close = open !== null && resultUsd !== null && contribution !== null && withdrawal !== null ? open + resultUsd + contribution - withdrawal : null;
      if (close !== null && (!finite(close) || !finite(resultUsd) || close < 0)) { issues.push('Saldo final negativo ou fora do limite.'); close = null; }
      if (!finite(resultUsd)) resultUsd = null;
      if (!finite(rate)) rate = null;
      const finalized = !options.reference && continuous && requestedClose && closure.confirmFlows === true
        && hasResult && !provisional && close !== null && !issues.length && month <= today;
      if (requestedClose && !finalized) issues.push('Fechamento requer sequência contínua, resultado válido e conferência dos fluxos.');
      continuous = finalized;
      const phase = finalized ? 'confirmed' : month < today ? 'pending' : month === today ? 'current' : 'projected';
      const historical = object(options.historicalQuotes) ? options.historicalQuotes[month] : null;
      const matching = validQuote(historical) && historical.referenceDate.slice(0, 7) === month ? historical.rate : null;
      const fxRate = finalized && validQuote(closure.fxQuote) ? closure.fxQuote.rate : month < today ? matching : (validQuote(options.quote) ? options.quote.rate : null);
      const brl = close !== null && fxRate !== null ? close * fxRate : null;
      rows.push({ month, openUsd: open, rate, resultUsd, contributionUsd: contribution, withdrawalUsd: withdrawal,
        closeUsd: close, phase, finalized, provisional, fxRate, closeBrl: finite(brl) ? brl : null,
        referenceCloseUsd: plan.reference && Array.isArray(plan.reference.rows) && plan.reference.rows[i] ? plan.reference.rows[i].closeUsd : options.reference ? close : null,
        plannedContributionUsd: planned, contributionBlank,actualContributionUsd: ledgerContribution,
        contributionSource: usePlanned ? 'projected' : 'recorded', resultSource: hasResult ? 'recorded' : 'projected', issues });
      open = close;
    }
    return rows;
  }

  function confirmedSummary(plan, rows) {
    const closed = [];
    for (const row of rows) { if (!row.finalized) break; closed.push(row); }
    const sum = key => closed.reduce((n, r) => n + r[key], 0);
    return { confirmedThrough: closed.length ? closed[closed.length - 1].month : null,
      confirmed: { balanceUsd: closed.length ? closed[closed.length - 1].closeUsd : null,
        initialUsd: plan.initialUsd, contributionsUsd: sum('contributionUsd'), resultUsd: sum('resultUsd'), withdrawalsUsd: sum('withdrawalUsd') } };
  }
  function goalReadModel(plan, rows, referenceRows, today) {
    const goals = {};
    for (const key of ['adequate', 'ideal']) {
      const goal = plan.goals && plan.goals[key], initialGoals=plan.incomeBaselineGoals || plan.reference?.config?.goals, initial=initialGoals&&initialGoals[key];
      const usd = goal && finite(goal.usd) ? goal.usd : null, initialUsd = initial && finite(initial.usd) ? initial.usd : null;
      const found = usd > 0 ? rows.find(r => finite(r.resultUsd) && r.resultUsd >= usd) : null;
      const ref = initialUsd > 0 ? referenceRows.find(r => finite(r.resultUsd) && r.resultUsd >= initialUsd) : null;
      const goalChanged = usd !== null && (initialUsd === null || Math.abs(usd - initialUsd) > .005);
      const invalid = rows.some(r => r.closeUsd === null || r.resultUsd === null);
      const p = profile(plan.profileId), required = usd > 0 && p && p.rate > 0 ? Math.ceil((usd / p.rate - 1e-9) * 100) / 100 : null;
      goals[key] = { usd, initialUsd, month: found ? found.month : null, referenceMonth: ref ? ref.month : null,
        status: usd === null ? 'NOT_INFORMED' : invalid ? 'PENDING_DATA' : !found ? 'NOT_REACHED' : found.finalized ? 'ACHIEVED' : 'PROJECTED',
        goalChanged, deltaMonths: !goalChanged && found && ref ? ordinal(found.month) - ordinal(ref.month) : null,
        remainingMonths: found ? Math.max(0, ordinal(found.month) - ordinal(today)) : null,
        waitingForClosure: !!found && !found.finalized && found.month < today,
        requiredCapitalUsd: finite(required) ? required : null, durationMonths: found ? ordinal(found.month) - ordinal(plan.startMonth) + 1 : null,
        durationText:found?durationText(ordinal(found.month)-ordinal(plan.startMonth)+1):'' };
    }
    return goals;
  }
  function average(plan, today) {
    let totalUsd = 0, knownUsd = 0, cost = 0;
    for (const c of Array.isArray(plan.contributions) ? plan.contributions : []) {
      if (!object(c) || c.month > today || !finite(c.usd) || c.usd <= 0) continue;
      totalUsd += c.usd;
      if (finite(c.brl) && c.brl > 0) { knownUsd += c.usd; cost += c.brl; }
    }
    return { rate: knownUsd > 0 ? cost / knownUsd : null, knownUsd, totalUsd, coverage: totalUsd > 0 ? knownUsd / totalUsd : null };
  }
  function annual(rows) {
    const groups = [];
    rows.forEach(row => {
      const year = row.month.slice(0, 4);
      let g = groups[groups.length - 1];
      if (!g || g.year !== year) { g = { year, months: 0, openUsd: row.openUsd, closeUsd: null, rate: 0, resultUsd: 0, contributionUsd: 0, withdrawalUsd: 0,
        contributionSource: row.contributionSource, resultSource: row.resultSource, provisional: false, finalized: true }; groups.push(g); }
      g.months++; g.closeUsd = row.closeUsd; g.finalized = g.finalized && row.finalized;
      g.provisional = g.provisional || row.provisional === true;
      for (const source of ['contributionSource', 'resultSource']) if (g[source] !== row[source]) g[source] = 'mixed';
      g.rate = g.rate === null || row.rate === null ? null : (1 + g.rate) * (1 + row.rate) - 1;
      for (const key of ['resultUsd', 'contributionUsd', 'withdrawalUsd']) g[key] = g[key] === null || row[key] === null ? null : g[key] + row[key];
    });
    return groups;
  }
  function account(value, options) {
    options = options || {};
    if (!object(value) || !object(value.plan)) return { id: value && value.id || null, name: value && value.name || '', planId: null, rows: [], referenceRows: [], confirmedThrough: null,
      confirmed: { balanceUsd: null, contributionsUsd: 0, resultUsd: 0, withdrawalsUsd: 0, initialUsd: null }, goals: {}, priceAverage: { rate: null, knownUsd: 0, totalUsd: 0, coverage: null }, status: 'INVALID', issues: ['Conta ou plano inválido.'], annual: [] };
    const p = value.plan, rows = timeline(p, options), today = monthKey(options.month) || p.startMonth;
    const referenceRows = p.reference && Array.isArray(p.reference.rows) ? clone(p.reference.rows) : [];
    const issues = rows.flatMap(r => r.issues.map(i => r.month + ': ' + i));
    if (!rows.length) issues.push('Calendário inválido.');
    return Object.assign({ id: value.id, name: value.name, planId: p.id, rows, referenceRows,
      goals: goalReadModel(p, rows, referenceRows, today), priceAverage: average(p, today), annual: annual(rows),
      status: rows.some(r => r.closeUsd === null) || !rows.length ? 'INVALID' : rows.some(r => r.provisional) ? 'PROVISIONAL' : 'READY', issues }, confirmedSummary(p, rows));
  }

  function portfolio(envelope, options) {
    options = options || {};
    const errors = validateEnvelope(envelope);
    if (errors.length) return { accounts: [], rows: [], referenceRows: [], confirmedThrough: null,
      confirmed: { balanceUsd: null, initialUsd: null, contributionsUsd: 0, resultUsd: 0, withdrawalsUsd: 0 },
      priceAverage: { rate: null, knownUsd: null, totalUsd: null, coverage: null }, annual: [], goals: null, status: 'INVALID', issues: errors };
    const list = envelope && Array.isArray(envelope.accounts) ? envelope.accounts : [];
    const selected = list.filter(a => object(a) && (options.accountId ? a.id === options.accountId : a.active === true));
    const accounts = selected.map(a => account(a, options)), populated = accounts.filter(a => a.rows.length);
    const rows = [], referenceRows = [];
    if (populated.length) {
      const start = Math.min(...populated.map(a => ordinal(a.rows[0].month)));
      const end = Math.max(...populated.map(a => ordinal(a.rows[a.rows.length - 1].month)));
      function consolidated(key, at) {
        const month = addMonths(populated[0].rows[0].month, at - ordinal(populated[0].rows[0].month));
        const today = monthKey(options.month) || month;
        const historical = object(options.historicalQuotes) ? options.historicalQuotes[month] : null;
        const fx = month < today ? validQuote(historical) && historical.referenceDate.slice(0, 7) === month ? historical.rate : null : validQuote(options.quote) ? options.quote.rate : null;
        const points = populated.map(a => {
          const series = a[key], first = series[0], last = series[series.length - 1];
          if (!first || at < ordinal(first.month)) return null;
          if (at > ordinal(last.month)) return { openUsd: last.closeUsd, closeUsd: last.closeUsd, rate: 0, resultUsd: 0, contributionUsd: 0, withdrawalUsd: 0,
            // Original Formulario545–549: preserve the terminal position and
            // zero flows, never fabricate another confirmed monthly closure.
            finalized: false, carried: true, knownPosition: key === 'rows' && last.finalized,
            contributionSource: 'projected', resultSource: 'projected',
            fxRate: fx, closeBrl: fx !== null && finite(last.closeUsd) && finite(last.closeUsd * fx) ? last.closeUsd * fx : null, provisional: false, issues: [] };
          return series[at - ordinal(first.month)];
        }).filter(Boolean);
        const sum = field => {
          const amount = points.every(p => finite(p[field])) ? points.reduce((n, p) => n + p[field], 0) : null;
          return finite(amount) ? amount : null;
        };
        const openUsd = sum('openUsd'), closeUsd = sum('closeUsd'), resultUsd = sum('resultUsd');
        const finalized = month <= today && points.length > 0 && points.every(p => p.finalized);
        const source = key => points.every(p => p[key] === 'recorded') ? 'recorded' : points.every(p => p[key] === 'projected') ? 'projected' : 'mixed';
        return { month, openUsd, resultUsd, contributionUsd: sum('contributionUsd'), withdrawalUsd: sum('withdrawalUsd'), closeUsd,
          rate: openUsd === null || resultUsd === null ? null : openUsd > 0 ? resultUsd / openUsd : resultUsd === 0 ? 0 : null,
          finalized, phase: finalized ? 'confirmed' : month < today ? 'pending' : month === today ? 'current' : 'projected',
          provisional: points.some(p => p.provisional), fxRate: finalized ? null : fx,
          carriedAccounts: points.filter(p => p.carried).length,
          contributionSource: source('contributionSource'), resultSource: source('resultSource'),
          closeBrl: finalized ? sum('closeBrl') : closeUsd !== null && fx !== null && finite(closeUsd * fx) ? closeUsd * fx : null,
          referenceCloseUsd: null, issues: points.flatMap(p => p.issues || []) };
      }
      for (let at = start; at <= end; at++) {
        const row = consolidated('rows', at), ref = consolidated('referenceRows', at);
        row.referenceCloseUsd = ref.closeUsd; rows.push(row); referenceRows.push(ref);
      }
    }
    const closed = [];
    for (const r of rows) { if (!r.finalized) break; closed.push(r); }
    const last = closed[closed.length - 1];
    const confirmed = { balanceUsd: last ? last.closeUsd : null,
      initialUsd: selected.filter(a => !last || a.plan.startMonth <= last.month).reduce((n, a) => n + (finite(a.plan.initialUsd) ? a.plan.initialUsd : 0), 0),
      contributionsUsd: closed.reduce((n, r) => n + r.contributionUsd, 0), resultUsd: closed.reduce((n, r) => n + r.resultUsd, 0), withdrawalsUsd: closed.reduce((n, r) => n + r.withdrawalUsd, 0) };
    const acquisitionMonth = monthKey(options.month) || (rows.length ? rows[0].month : '0000-01');
    const priceAverage = average({ contributions: selected.flatMap(a => a.plan.contributions) }, acquisitionMonth);
    return { accounts, rows, referenceRows, confirmedThrough: last ? last.month : null, confirmed, priceAverage, annual: annual(rows), goals: null,
      status: errors.length ? 'INVALID' : !accounts.length ? 'EMPTY' : accounts.some(a => a.status === 'INVALID') ? 'INVALID' : accounts.some(a => a.status === 'PROVISIONAL') ? 'PROVISIONAL' : 'READY',
      issues: errors.concat(accounts.flatMap(a => a.issues)) };
  }

  function stopBounds(plan, options) {
    options = options || {};
    if (!object(plan) || typeof plan.startMonth !== 'string' || !monthKey(plan.startMonth)) throw new TypeError('Início do plano inválido.');
    if (own(options, 'month') && !monthKey(options.month)) throw new TypeError('Mês de referência inválido.');
    const first = ordinal(plan.startMonth), end = first + 119;
    const today = ordinal(monthKey(options.month) || plan.startMonth);
    // Native Parada75 permits start-1 before a future plan, and caps the
    // minimum at the final month for a plan whose horizon has already ended.
    return { min: options.newPlan===true?addMonths(plan.startMonth,-1):addMonths(plan.startMonth, Math.max(first - 1, Math.min(today, end)) - first), max: addMonths(plan.startMonth, 119) };
  }
  function withContributionStop(plan, options) {
    options = options || {};
    if(options.newPlan===true&&(Object.keys(plan.results||{}).length||(plan.contributions||[]).length||(plan.withdrawals||[]).length||Object.values(plan.closures||{}).some(c=>c.confirmed)))throw new TypeError('A simulação de novo plano não aceita lançamentos existentes.');
    const bounds = stopBounds(plan, options), stopAfter = options.stopAfter;
    if (stopAfter !== null && (!monthKey(stopAfter) || stopAfter < bounds.min || stopAfter > bounds.max)) throw new TypeError('Mês da parada inválido: respeite o mês atual e o horizonte do plano.');
    const candidate = clone(plan), today = monthKey(options.month) || plan.startMonth;
    candidate.stopAfter = stopAfter;
    candidate.future = object(candidate.future) ? candidate.future : {};
    if (stopAfter !== null) for (let i = 0; i < 120; i++) {
      const month = addMonths(plan.startMonth, i);
      if (month > stopAfter && (options.newPlan===true || month > today)) candidate.future[month] = Object.assign({}, candidate.future[month] || {}, { contributionUsd: 0 });
    }
    return candidate;
  }
  function checkImpactLimit(value) {
    if (!finite(value) || value < 0 || value > 1) throw new TypeError('Escolha um limite de impacto entre0% e100%.');
  }
  function simulate(plan, options) {
    options = options || {};
    stopBounds(plan, options);
    const today = monthKey(options.month) || plan.startMonth;
    if (options.increaseUsd !== undefined && (!nonnegative(options.increaseUsd))) throw new TypeError('Aumento de aporte inválido.');
    if (options.increasePct !== undefined && (!finite(options.increasePct) || options.increasePct < 0)) throw new TypeError('Aumento percentual inválido.');
    if (options.fromMonth !== undefined && !monthKey(options.fromMonth)) throw new TypeError('Mês do aumento inválido.');
    if (own(options, 'impactLimit')) checkImpactLimit(options.impactLimit);
    const baseRows = timeline(plan, options);
    let draft = clone(plan);
    draft.future = object(draft.future) ? draft.future : {};
    if (options.increaseUsd !== undefined || options.increasePct !== undefined) baseRows.forEach(row => {
      if (row.finalized || row.month <= today || row.month < (options.fromMonth || plan.startMonth)) return;
      const future = draft.future[row.month] = Object.assign({}, draft.future[row.month] || {});
      let amount = row.plannedContributionUsd;
      if (!finite(amount)) return;
      amount += options.increaseUsd || 0;
      amount *= 1 + (options.increasePct || 0) / 100;
      // Simulation compounds full precision; stored entry cents remain a command concern.
      future.contributionUsd = amount;
    });
    // The stop is applied after an optional increase, through the same pure
    // candidate builder used by the save command. Existing zeros stay zero.
    if (own(options, 'stopAfter')) draft = withContributionStop(draft, options);
    // Fractional cents from a percentage increase are simulation values, so apply
    // them as finite nonnegative model inputs without writing ledger entries.
    const rows = timeline(draft, Object.assign({}, options, { simulation: true }));
    const finalUsd = rows.length ? rows[rows.length - 1].closeUsd : null;
    const baselineFinalUsd = baseRows.length ? baseRows[baseRows.length - 1].closeUsd : null;
    const effectUsd = finite(finalUsd) && finite(baselineFinalUsd) ? finalUsd - baselineFinalUsd : null;
    const effectRate = effectUsd !== null && baselineFinalUsd > 0 ? effectUsd / baselineFinalUsd : null;
    const impactRate = effectRate === null ? null : Math.max(0, -effectRate);
    const viable = finite(finalUsd) && !rows.some(r => r.closeUsd === null);
    const projected = row => row.contributionSource === 'projected' ? row.contributionUsd : 0;
    const savedContributionsUsd = baseRows.every((row, i) => finite(projected(row)) && finite(projected(rows[i])))
      ? baseRows.reduce((sum, row, i) => sum + projected(row) - projected(rows[i]), 0) : null;
    const reference = plan.reference && Array.isArray(plan.reference.rows) ? plan.reference.rows : [];
    const issues = rows.flatMap(r => r.issues.map(i => r.month + ': ' + i));
    return { rows, baseRows, goals: goalReadModel(draft, rows, reference, today), baseGoals: goalReadModel(plan, baseRows, reference, today),
      finalUsd, baselineFinalUsd, effectUsd, effectRate, impactRate,
      withinImpactLimit: own(options, 'impactLimit') && impactRate !== null ? viable && impactRate <= options.impactLimit + 1e-10 : null,
      appliedOrder: ['increase', 'stop'].filter(key => key === 'stop' ? own(options, 'stopAfter') : options.increaseUsd !== undefined || options.increasePct !== undefined),
      savedContributionsUsd, differenceUsd:finite(finalUsd)&&finite(baselineFinalUsd)?baselineFinalUsd-finalUsd:null,
      dispensedMonthsCount:baseRows.filter((row,i)=>finite(projected(row))&&finite(projected(rows[i]))&&projected(row)>projected(rows[i])).length,
      viable, provisional: rows.some(r => r.provisional),
      status: rows.some(r => r.closeUsd === null) ? 'INVALID' : rows.some(r => r.provisional) ? 'PROVISIONAL' : 'SIMULATED', issues };
  }
  function findContributionStop(plan, options) {
    options = options || {};
    checkImpactLimit(options.impactLimit);
    const bounds = stopBounds(plan, options), first = ordinal(bounds.min), last = ordinal(bounds.max);
    for (let at = first; at <= last; at++) {
      const stopAfter = addMonths(bounds.min, at - first);
      const result = simulate(plan, Object.assign({}, options, { stopAfter }));
      if (result.withinImpactLimit === true) return { stopAfter, result, impactLimit: options.impactLimit };
    }
    return null;
  }

  // Read-only presentation contract traced to the native Sheet's cells and
  // Apps Script. All amounts still come from this engine, never from the DOM.
  function profileView(id) {
    const p = profile(id); if (!p) return null;
    const curve = limit => Array.from({length: limit + 1}, (_, n) => ({loss:n / 100, gain:n / (100 - n)}));
    return Object.assign({}, p, {recoveryRate:p.mdd / (1 - p.mdd),
      growth:Array.from({length:13}, (_, month) => ({month, value:100 * (1 + p.rate) ** month, rate:(1 + p.rate) ** month - 1})),
      recoveryCurve50:curve(50), recoveryCurve95:curve(95)});
  }
  function contributionWeights(rate, count) {
    if (!finite(rate) || rate < -1 || !Number.isInteger(count) || count < 5) throw new TypeError('Premissas do exemplo inválidas.');
    const first = Math.ceil(count * .2), last = count - first;
    const groups = ['Primeiros 20%', 'Etapa intermediária', 'Últimos 20%'].map(name => ({name, value:0, share:0}));
    for (let i=0;i<count;i++) groups[i<first?0:i>=last?2:1].value += (1+rate) ** (count-1-i);
    const total = groups.reduce((n,g) => n+g.value,0);
    groups.forEach(g => {g.share=total>0?g.value/total:0;}); return groups;
  }
  function formView(config, options) {
    options = options || {};
    const prepared=clone(config),available={};
    prepared.goals={};
    for(const key of ['adequate','ideal']){
      try{available[key]=normalizeGoal(config.goals&&config.goals[key],key==='ideal');}catch(_error){available[key]=null;}
      prepared.goals[key]=available[key] || (key==='ideal'?{value:1,currency:'USD'}:null);
    }
    const plan = createPlan(prepared, {id:'form-preview', now:options.now || '2026-01-01T00:00:00.000Z'});
    // The form's forecast uses the initial fixed plan, including when its
    // chosen start predates today; this is not the current recorded ledger.
    const model = account({id:'form-preview',name:config.name || 'Conta de investimento',plan}, {month:plan.startMonth,quote:options.quote});
    for(const key of ['adequate','ideal']){
      if(!available[key]){model.goals[key]=null;continue;}
      // Original form preview has its own 1e-8 threshold tolerance. Prazos
      // (recorded monthly trajectory) intentionally keeps its strict >= test.
      const found=model.rows.find(r=>r.resultUsd+1e-8>=available[key].usd),g=model.goals[key];
      g.month=found?.month||null;g.durationMonths=found?ordinal(found.month)-ordinal(plan.startMonth)+1:null;
      g.durationText=found?durationText(g.durationMonths):'';
    }
    return {plan,model,goals:model.goals,adequateUsd:available.adequate?.usd??null,idealUsd:available.ideal?.usd??null,
      requiredCapitalUsd:model.goals.ideal?.requiredCapitalUsd??null,
      profile:profileView(plan.profileId), contributionWeights:contributionWeights(profile(plan.profileId).rate,120)};
  }
  function durationText(months){
    if(months===1)return '1º mês do plano';const years=Math.floor(months/12),rest=months%12;
    return (years?years+(years===1?' ano':' anos'):'')+(years&&rest?' e ':'')+(rest?rest+(rest===1?' mês':' meses'):'');
  }
  function revisePlan(plan, config, options) {
    options = options || {};
    const replacement=createPlan(config,{id:plan.id,now:options.now||plan.reference.createdAt});
    const today=monthKey(options.month)||plan.startMonth, previous=clone(plan), next=clone(plan);
    next.startMonth=replacement.startMonth; next.initialUsd=replacement.initialUsd;
    next.profileId=replacement.profileId; next.monthlyContributionUsd=replacement.monthlyContributionUsd;
    next.goals=replacement.goals; next.future={};
    // Native cells hold their own values. Editing the form without Reaplicar
    // cannot silently change cells which formerly used the profile defaults.
    for(let i=0;i<120;i++){
      const oldMonth=addMonths(previous.startMonth,i),month=addMonths(next.startMonth,i),old=previous.future[oldMonth]||{};
      const reapply=options.replaceFuture===true&&month>today&&!previous.closures[oldMonth]?.confirmed;
      next.future[month]=Object.assign({},old,{rate:reapply?profile(next.profileId).rate:own(old,'rate')?old.rate:profile(previous.profileId).rate,
        contributionUsd:reapply?next.monthlyContributionUsd:own(old,'contributionUsd')?old.contributionUsd:previous.stopAfter&&oldMonth>previous.stopAfter?0:previous.monthlyContributionUsd});
    }
    return next;
  }
  function formStopPlan(config, options) {
    options=options||{};
    const valid=config&&monthKey(config.startMonth)&&premiseAmount(config.initialUsd)&&premiseAmount(config.monthlyContributionUsd||0)&&profile(config.profileId);
    const c=valid?Object.assign({},config):{startMonth:'2026-01',initialUsd:100000,monthlyContributionUsd:300,profileId:'base'};
    c.monthlyContributionUsd=c.monthlyContributionUsd||0;
    // Income is not an input of this educational comparison.
    c.goals={adequate:null,ideal:{value:1,currency:'USD'}};
    const previous=valid&&options.account&&options.account.plan;
    const plan=previous&&!options.newPlan?revisePlan(previous,c,options):createPlan(c,{id:'stop-preview',now:'2026-01-01T00:00:00.000Z'});
    return {plan,didactic:!valid,newPlan:!previous||options.newPlan===true||!valid};
  }
  function sheetView(envelope, options) {
    options = options || {};
    const issues = validateEnvelope(envelope);
    if (issues.length) return {status:'INCOMPATIBLE',issues,rows:[],sheet:null};
    const accounts = (envelope.accounts || []).filter(a => a.active === true);
    const selected = options.accountId ? accounts.find(a => a.id === options.accountId) : null;
    if (options.accountId && !selected) return {status:'NOT_FOUND',issues:['Conta não encontrada.'],rows:[],sheet:null};
    const model = selected ? account(selected, options) : portfolio(envelope,options);
    const single = selected || (accounts.length === 1 ? accounts[0] : null);
    const individual = single ? account(single, options) : null;
    // Prazos G1: a single active account supplies individual goals even under
    // Todas as contas. Multiple personal income targets are never added.
    model.goals = individual ? individual.goals : null;
    const rows = model.rows || [], today = monthKey(options.month) || rows[0]?.month || '2026-01';
    const years = Array.from(new Set(rows.map(r=>Number(r.month.slice(0,4)))));
    const requestedYear = Number(options.projectionYear);
    const year = years.includes(requestedYear) ? requestedYear : years[years.length-1] || null;
    const projected = rows.filter(r=>Number(r.month.slice(0,4))===year).slice(-1)[0] || null;
    const chartOptions = [{id:'full',label:'Plano completo'}, {id:'current-year',label:'Ano atual'},
      ...[[3,'Próximos 3 meses'],[6,'Próximos 6 meses'],[12,'Próximos 12 meses'],[24,'Próximos 2 anos'],[36,'Próximos 3 anos'],[60,'Próximos 5 anos'],[120,'Próximos 10 anos']].map(x=>({id:'next:'+x[0],label:x[1]})),
      ...[[3,'Últimos 3 meses'],[6,'Últimos 6 meses'],[12,'Últimos 12 meses']].map(x=>({id:'last:'+x[0],label:x[1]})),
      ...years.map(y=>({id:'year:'+y,label:'Ano '+y}))];
    let chosen = chartOptions.find(p=>p.id===options.chartPeriod || p.label===options.chartPeriod) || chartOptions[0];
    let begin = rows[0]?.month || today, end = rows.length ? addMonths(rows[rows.length-1].month,1) : today;
    if(chosen.id==='current-year'){begin=today.slice(0,4)+'-01';end=addMonths(begin,12);}
    if(chosen.id.startsWith('year:')){begin=chosen.id.slice(5)+'-01';end=addMonths(begin,12);}
    if(chosen.id.startsWith('next:')){begin=today;end=addMonths(begin,Number(chosen.id.slice(5)));}
    if(chosen.id.startsWith('last:')){begin=addMonths(today,1-Number(chosen.id.slice(5)));end=addMonths(today,1);}
    let contributions=0;
    const completeChartRows = rows.map(r=>{
      contributions = contributions===null || !finite(r.contributionUsd) ? null : contributions+r.contributionUsd;
      return Object.assign({},r,{cumulativeContributionUsd:contributions,
        confirmedUsd:r.finalized?r.closeUsd:null, pendingUsd:r.month<=today&&!r.finalized?r.closeUsd:null,
        projectedUsd:r.month>=today?r.closeUsd:null});
    });
    const chartRows=completeChartRows.filter(r=>r.month>=begin&&r.month<end);
    const realChartOptions=['Patrimônio e aportes (US$)','Rentabilidade mensal (%)','Aportes do mês (US$)','Saques do mês (US$)'];
    const realChartMode=realChartOptions.includes(options.realChartMode)?options.realChartMode:'Rentabilidade mensal (%)';
    const realKey=realChartMode==='Rentabilidade mensal (%)'?'rate':realChartMode==='Aportes do mês (US$)'?'contributionUsd':realChartMode==='Saques do mês (US$)'?'withdrawalUsd':'closeUsd';
    const realChartRows=completeChartRows.filter(r=>r.finalized).map(r=>Object.assign({},r,{value:r[realKey],secondaryValue:realKey==='closeUsd'?r.cumulativeContributionUsd:null}));
    const tableMode = options.tableMode || 'Anual · Resumo completo';
    const selectedIndicator = options.indicator || (tableMode.includes('Aportes')?'Aporte do mês':tableMode.includes('Resultado')?'Resultado do mês':tableMode.includes('Rentabilidade')?'Rentabilidade':'Patrimônio');
    const indicator=selectedIndicator==='Resultado'?'Resultado do mês':selectedIndicator==='Aportes'?'Aporte do mês':selectedIndicator;
    const tableStart = Math.max(0,Math.min(years.indexOf(year),years.length-11)), tableYears=years.slice(tableStart,tableStart+11);
    const annualRows=(model.annual || []).filter(r=>tableYears.includes(Number(r.year))).map(r=>Object.assign({},r,{process:Number(r.year)<Number(today.slice(0,4))?'Encerrado':Number(r.year)===Number(today.slice(0,4))?'Em andamento':'Projetado'}));
    const names=['Janeiro','Fevereiro','Março','Abril','Maio','Junho','Julho','Agosto','Setembro','Outubro','Novembro','Dezembro'];
    const monthly=names.map((label,i)=>({month:i+1,label,values:tableYears.map(y=>{
      const r=rows.find(row=>row.month===y+'-'+String(i+1).padStart(2,'0'));
      const key=indicator==='Rentabilidade'?'rate':indicator==='Aporte do mês'?'contributionUsd':indicator==='Resultado do mês'?'resultUsd':'closeUsd';
      return {year:y,value:r&&finite(r[key])?r[key]:null};
    })}));
    const through=model.confirmedThrough, refRows=model.referenceRows || [];
    const aligned=rows.length===refRows.length&&rows.every((r,i)=>r.month===refRows[i].month);
    const point=through?refRows.find(r=>r.month===through):null;
    let comparisonStatus=!aligned?'Referência de outro plano':!through?'Sem fechamento confirmado':!point?'Comparativo pendente':'Comparável';
    const c=model.confirmed || {};
    const plannedContributions=through?refRows.filter(r=>r.month<=through).reduce((n,r)=>finite(n)&&finite(r.contributionUsd)?n+r.contributionUsd:null,0):null;
    const comparisonRows=[['Patrimônio',point?.closeUsd,c.balanceUsd],['Aportes acumulados',plannedContributions,c.contributionsUsd]].map(([label,planned,confirmed])=>{
      const valid=comparisonStatus==='Comparável'&&finite(planned)&&finite(confirmed);
      const delta=valid?Math.round((confirmed-planned)*100)/100:null;
      return {label,planned:valid?planned:null,confirmed:valid?confirmed:null,deviationUsd:delta,deviationRate:valid&&planned>0?delta/planned:null};
    });
    if(comparisonStatus==='Comparável'&&comparisonRows.some(r=>r.deviationUsd===null))comparisonStatus='Comparativo pendente';
    const latestQuote=validQuote(options.quote)?options.quote.rate:null;
    const sourceAccounts=selected?[selected]:accounts;
    let knownUsd=0,totalUsd=0,totalBrl=0;
    const monthlyRows=rows.map((r,index)=>{
      let paidBrl=0,monthlyKnown=false;
      for(const a of sourceAccounts)for(const flow of a.plan.contributions || [])if(flow.month===r.month&&flow.month<=today&&flow.usd>0){
        totalUsd+=flow.usd;
        if(finite(flow.brl)&&flow.brl>0){knownUsd+=flow.usd;totalBrl+=flow.brl;paidBrl+=flow.brl;monthlyKnown=true;}
      }
      const averageRate=r.month<=today&&knownUsd>0?totalBrl/knownUsd:null;
      const quoteValue=r.month<=today?latestQuote:null;
      const coverage=totalUsd>0?knownUsd/totalUsd:null;
      let costStatus=r.month>today?(r.contributionBlank?'Sem aporte previsto':'Aporte projetado'):totalUsd>0?Math.round(coverage*100)+'% do custo informado':'Sem compras registradas';
      if(r.month<=today&&r.contributionSource==='projected'&&r.contributionUsd>0)costStatus+=' · Aporte não confirmado: expira ao fim do mês';
      return Object.assign({},r,{cyclePhase:Math.floor(index/12)+1,situation:r.finalized?'Realizado':r.provisional||r.closeUsd===null?'Pendente':r.month>today?'Projeção':r.month===today?'Em andamento':'Pendente',
        resultBrl:finite(r.resultUsd)&&finite(r.fxRate)?r.resultUsd*r.fxRate:null,
        paidBrl:monthlyKnown?paidBrl:null, averageRate,quoteRate:quoteValue,
        fxVariation:averageRate>0&&quoteValue>0?quoteValue/averageRate-1:null,costCoverage:coverage,costStatus});
    });
    const ref=single?.plan?.reference, rc=ref?.config;
    // Native Mensal rows17/30/... contain a subtotal after each group of
    // twelve plan months, which need not coincide with a calendar year.
    const phaseTotals=[];
    for(let i=0;i<monthlyRows.length;i+=12){
      const block=monthlyRows.slice(i,i+12);if(!block.length)continue;
      const first=block[0],last=block[block.length-1],sum=key=>block.every(r=>finite(r[key]))?block.reduce((n,r)=>n+r[key],0):null;
      const startYear=first.month.slice(0,4),endYear=last.month.slice(0,4);
      phaseTotals.push({cyclePhase:Math.floor(i/12)+1,label:startYear===endYear?startYear:startYear+'–'+endYear,
        monthLabel:first.month.endsWith('-01')?'FECHAMENTO':'12 MESES',startMonth:first.month,endMonth:last.month,openUsd:first.openUsd,
        resultUsd:sum('resultUsd'),resultBrl:sum('resultBrl'),fxRate:last.fxRate,withdrawalUsd:sum('withdrawalUsd'),contributionUsd:sum('contributionUsd'),
        closeUsd:last.closeUsd,closeBrl:last.closeBrl,situation:block.some(r=>r.situation==='Pendente')?'Pendente':block.every(r=>r.situation==='Realizado')?'Realizado':block.every(r=>r.situation==='Projeção')?'Projeção':'Misto'});
    }
    const gainWithIncrease=single?[5,10,15,20,25].map(increasePct=>({increasePct,...simulate(single.plan,Object.assign({},options,{increasePct}))})):[];
    model.sheet={summary:Object.assign({},c,{contributionsUsd:through?c.contributionsUsd:null,resultUsd:through?c.resultUsd:null,
        initialUsd:sourceAccounts.reduce((n,a)=>n+a.plan.initialUsd,0),averageRate:model.priceAverage?.rate??null,quoteRate:latestQuote}),
      projection:{year,month:projected?.month||null,closeUsd:projected?.closeUsd??null,closeBrl:projected?.closeBrl??null,years},
      chart:{period:chosen.id,options:chartOptions,rows:chartRows},realChart:{mode:realChartMode,options:realChartOptions.map(label=>({id:label,label})),rows:realChartRows},
      table:{mode:tableMode,indicator,years:tableYears,annual:annualRows,monthly},
      comparison:{status:comparisonStatus,through,rows:comparisonRows,message:comparisonStatus==='Comparável'?'Comparação no mesmo fechamento':comparisonStatus},
      goals:model.goals, gainWithIncrease,monthlyRows,phaseTotals,
      reference:ref?{version:ref.version,createdAt:ref.createdAt,closedAtSave:ref.closedAtSave??0,startMonth:rc.startMonth,endMonth:addMonths(rc.startMonth,119),initialUsd:rc.initialUsd,profileId:rc.profileId,monthlyContributionUsd:rc.monthlyContributionUsd,rows:ref.rows.map((r,i)=>Object.assign({},clone(r),{cumulativeContributionUsd:ref.rows.slice(0,i+1).reduce((n,row)=>n+row.contributionUsd,0)}))}:null};
    return model;
  }
  const namespace = root.JPWPlanning || (root.JPWPlanning = {});
  namespace.engine = Object.freeze({ profiles, startMonthRange, monthKey, addMonths, createPlan, validateEnvelope, timeline, account, portfolio, stopBounds, withContributionStop, simulate, findContributionStop, profileView, contributionWeights, formView, formStopPlan, revisePlan, sheetView });
})(window);
