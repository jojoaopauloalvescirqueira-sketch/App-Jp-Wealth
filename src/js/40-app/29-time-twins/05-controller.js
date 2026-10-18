(function (window) {
  'use strict';
  var ns = window.JPWTimeTwins = window.JPWTimeTwins || {};
  var instances = new Set();
  var moneyFormat = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' });
  function money(n) { return moneyFormat.format(Math.abs(n) < 0.005 ? 0 : n); }
  function percent(n) { return n === null ? 'sem base' : new Intl.NumberFormat('pt-BR', { style: 'percent', maximumFractionDigits: 2 }).format(Math.abs(n) < 0.00005 ? 0 : n); }
  function clone(v) { return JSON.parse(JSON.stringify(v)); }
  function storageHandle() { try { return window.localStorage; } catch (e) { return null; } }
  function mount(host) {
    if (!host || typeof host.appendChild !== 'function') throw new TypeError('Informe um contêiner para Gêmeos do Tempo.');
    var existing = host.__timeTwinsController;
    if (existing && !existing.snapshot().destroyed) return existing;
    var holder = document.createElement('div'); holder.innerHTML = ns.view.panelHTML();
    var root = holder.firstElementChild; host.appendChild(root);
    var sim = ns.simulation; var motionPreference = window.matchMedia ? window.matchMedia('(prefers-reduced-motion: reduce)') : null; var store = storageHandle(); var saved = ns.progress.read(store);
    var state = { mode: 'home', id: saved.value.currentMissionId, month: 0, active: false, running: false, destroyed: false, valid: true,
      prediction: null, reasonCorrect: false, helped: false, conflict: false, blocked: saved.blocked,
      progress: clone(saved.value), draft: null, applied: null, flags: {}, lever: 'prazo', actor: 'A', cohort: '',
      traceOpen: false, without: false, feedback: '', forecastFeedback: '', reasonFeedback: '', error: '', storageMessage: saved.error || '', continued: false };
    var raw = saved.raw; var projection = null; var prepared = null; var generation = 0; var frame = null; var lastTick = 0; var freeSettings = null; var changed = false; var crossChanged = false;
    function q(selector) { return root.querySelector(selector); }
    function field(name) { return q('[data-field="' + name + '"]'); }
    function out(name, text) { var el = q('[data-output="' + name + '"]'); if (el && el.textContent !== String(text)) el.textContent = text; }
    function action(name) { return q('[data-action="' + name + '"]'); }
    function hide(selector, hidden) { var el = q(selector); if (el) el.hidden = hidden; }
    function maxMonth() { return Math.max(state.applied.a.horizonMonths, state.applied.b.horizonMonths); }
    function completeMonth() { return state.applied && state.month >= maxMonth(); }
    function pause() {
      generation += 1;
      if (frame !== null) window.cancelAnimationFrame(frame);
      frame = null; state.running = false; state.continued = true;
      if (!state.destroyed && state.mode !== 'home') patch();
    }
    function invalidate() {
      pause(); state.prediction = null; state.reasonCorrect = false; state.month = 0;
      state.forecastFeedback = ''; state.reasonFeedback = ''; state.feedback = state.mode === 'free' ? 'Premissas atualizadas. Avance para observar.' : 'Prepare sua previsão para observar a nova tentativa.';
      state.traceOpen = false; state.without = false;
      if (state.mode === 'guided' && state.id === 'crossover') state.flags.crossInspected = false;
      if (field('prediction')) field('prediction').value = '';
      if (field('reason')) field('reason').value = '';
    }
    function freshFlags() { return { positiveObserved: false, zeroObserved: false, levers: {}, inspect: false, trace: false, without: false, calendarObserved: false, extraObserved: false, extraDates: [], dateChanged: false, rateChanged: false, crossInspected: false }; }
    function projectPair(pair) { return { a: sim.project(pair.a), b: sim.project(pair.b) }; }
    function checkpoint() {
      if (state.destroyed || !state.active || state.conflict || state.blocked) return;
      var result = ns.progress.write(state.progress, { storage: store, expectedRaw: raw });
      raw = result.raw; state.blocked = result.blocked;
      state.storageMessage = result.error || '';
      if (!result.ok && result.error && result.error.indexOf('Conflito:') === 0) { state.conflict = true; pause(); }
      patchProgress();
    }
    function patchProgress() {
      out('storage', state.storageMessage);
      action('reload').hidden = !state.conflict && !state.blocked;
      action('continue').hidden = Object.keys(state.progress.missions).length === 0 && state.progress.currentMissionId === ns.catalog.ids[0];
      var labels = { demonstrated: 'Demonstrada', assisted: 'Com explicação', skipped: 'Pulada' };
      ns.catalog.ids.forEach(function (id) {
        q('[data-status="' + id + '"]').textContent = labels[state.progress.missions[id]] || 'Por explorar';
        var b = q('[data-mission="' + id + '"]');
        if (state.mode === 'guided' && state.id === id) b.setAttribute('aria-current', 'step'); else b.removeAttribute('aria-current');
      });
    }
    function revealExercise(title) {
      title.focus({ preventScroll: true });
      var margin = parseFloat(window.getComputedStyle(title).scrollMarginTop) || 0;
      var target = title.getBoundingClientRect();
      // A submenu may extend outside its fixed header while remaining absolutely positioned.
      Array.prototype.forEach.call(document.querySelectorAll('body > header, #navSubShell, #toolsNavSubmenu'), function (obstruction) {
        var bounds = obstruction.getBoundingClientRect(); var style = window.getComputedStyle(obstruction);
        if (obstruction.closest('[hidden],[inert]') || style.display === 'none' || style.visibility === 'hidden' || !bounds.width || !bounds.height || bounds.bottom <= 0 || bounds.top >= window.innerHeight || bounds.left >= target.right || bounds.right <= target.left) return;
        var anchored = false;
        for (var parent = obstruction; parent && parent !== document.body; parent = parent.parentElement) {
          var position = window.getComputedStyle(parent).position;
          if (position === 'sticky' || position === 'fixed') { anchored = true; break; }
        }
        if (anchored) margin = Math.max(margin, bounds.bottom + 12);
      });
      title.style.scrollMarginTop = margin + 'px';
      // Native scrolling honors the actual overflow ancestors and their scroll padding.
      // Entry is explicit and instantaneous, including under reduced-motion preference.
      title.scrollIntoView({ block: 'start', inline: 'nearest', behavior: 'instant' });
    }
    function renderExercise() {
      q('[data-section="exercise"]').innerHTML = ns.view.exerciseHTML(state);
      hide('[data-section="home"]', true); hide('[data-section="exercise"]', false);
      if (field('lever')) field('lever').value = state.lever;
      field('actor').value = state.actor;
      if (state.mode === 'free') syncFreeFields();
      patch();
      var title = q('[data-output="title"]'); if (title && state.active) revealExercise(title);
    }
    function setup(mode, id, persist) {
      pause(); state.mode = mode; state.id = id || state.id; state.month = 0; state.flags = freshFlags(); state.lever = 'prazo';
      state.actor = 'A'; state.cohort = ''; state.prediction = null; state.reasonCorrect = false; state.helped = false; state.valid = true;
      state.error = ''; state.feedback = ''; state.forecastFeedback = ''; state.reasonFeedback = ''; state.traceOpen = false; state.without = false;
      state.continued = false; changed = false; crossChanged = false;
      if (mode === 'free') {
        state.draft = { a: sim.periodic({ id: 'A' }), b: sim.periodic({ id: 'B' }) };
        state.draft.baselineA = clone(state.draft.a); state.draft.baselineB = clone(state.draft.b);
        freeSettings = { A: { initial: 1000, monthly: 100, rate: 6, horizon: 240, start: 1, end: 240 }, B: { initial: 1000, monthly: 100, rate: 6, horizon: 240, start: 1, end: 240 } };
      } else state.draft = ns.catalog.create(state.id);
      state.applied = clone(state.draft); projection = projectPair(state.applied); prepared = projectPair(state.draft);
      if (mode === 'guided') { state.progress.currentMissionId = state.id; if (persist) checkpoint(); }
      renderExercise(); patchProgress();
    }
    function home() { pause(); state.mode = 'home'; hide('[data-section="home"]', false); hide('[data-section="exercise"]', true); patchProgress(); }
    function num(name) {
      var el = field(name); var value = el.value;
      if (value.trim() === '' || !el.checkValidity() || !Number.isFinite(Number(value))) throw new RangeError('Revise os campos: use valores nos limites indicados e dinheiro com até duas casas decimais.');
      return Number(value);
    }
    function singleDepositPair() {
      var draft = clone(state.draft);
      ['A', 'B'].forEach(function (actor) {
        var scenario = draft[actor.toLowerCase()]; var month = num(actor + '-deposit');
        scenario.initialCapital = month === 0 ? 1000 : 0;
        scenario.contributions = month === 0 ? [] : [{ id: actor === 'B' ? 'B-month-60' : 'A-capital', month: month, amount: 1000 }];
      });
      return draft;
    }
    function syncFreeFields() {
      ['A', 'B'].forEach(function (actor) { var cfg = freeSettings[actor]; Object.keys(cfg).forEach(function (k) { field(actor + '-' + k).value = cfg[k]; }); field(actor + '-start').max = cfg.horizon; field(actor + '-end').max = cfg.horizon; });
    }
    function edit(target) {
      if (state.mode === 'home' || state.destroyed) return;
      var key = target.dataset.field;
      if (!key || !/^[AB]-/.test(key)) return;
      invalidate();
      try {
        var draft = clone(state.draft); var m = state.mode === 'free' ? 'free' : state.id;
        if (m === 'free') {
          var next = clone(freeSettings);
          ['A', 'B'].forEach(function (actor) {
            var h = num(actor + '-horizon'); var old = freeSettings[actor];
            if (key === actor + '-horizon' && Number(field(actor + '-end').value) === old.horizon) field(actor + '-end').value = h;
            field(actor + '-start').max = h; field(actor + '-end').max = h;
            ['initial', 'monthly', 'rate', 'horizon', 'start', 'end'].forEach(function (k) { next[actor][k] = num(actor + '-' + k); });
            var cfg = next[actor];
            draft[actor.toLowerCase()] = sim.periodic({ id: actor, initialCapital: cfg.initial, monthlyContribution: cfg.monthly, annualRate: cfg.rate / 100, horizonMonths: cfg.horizon, startMonth: cfg.start, endMonth: cfg.end });
          });
          freeSettings = next;
        } else if (m === 'early-start') {
          draft = singleDepositPair();
        } else if (m === 'equal-budget') {
          var base = ns.catalog.create(m);
          ['A', 'B'].forEach(function (actor) { var s = draft[actor.toLowerCase()]; var start = num(actor + '-start'); s.contributions = base[actor.toLowerCase()].contributions.map(function (c, index) { return { id: c.id, month: start + index, amount: c.amount }; }); });
        } else if (m === 'three-levers') {
          var preset = ns.catalog.create(m);
          ['A', 'B'].forEach(function (actor) { var s = preset[actor.toLowerCase()]; draft[actor.toLowerCase()] = sim.periodic({ id: actor, initialCapital: s.initialCapital, monthlyContribution: state.lever === 'aporte' ? num(actor + '-monthly') : 100, annualRate: state.lever === 'taxa' ? num(actor + '-rate') / 100 : .06, horizonMonths: state.lever === 'prazo' ? num(actor + '-horizon') : 240 }); });
        } else if (m === 'next-contribution') {
          ['A', 'B'].forEach(function (actor) { var s = draft[actor.toLowerCase()]; s.contributions.find(function (c) { return c.id === actor + '-extra'; }).month = num(actor + '-extra'); });
        } else if (m === 'crossover') {
          ['A', 'B'].forEach(function (actor) { draft[actor.toLowerCase()].annualRate = num(actor + '-rate') / 100; });
        }
        var calculated = projectPair(draft); state.draft = draft; prepared = calculated; state.valid = true; state.error = '';
        var original = m === 'free' ? null : ns.catalog.create(m);
        changed = original ? JSON.stringify(draft.a) !== JSON.stringify(original.a) || JSON.stringify(draft.b) !== JSON.stringify(original.b) : false;
        if (m === 'crossover') crossChanged = draft.a.annualRate !== original.a.annualRate || draft.b.annualRate !== original.b.annualRate;
        if (m === 'equal-budget') state.flags.calendarObserved = false;
        if (m === 'three-levers') delete state.flags.levers[state.lever];
        if (m === 'crossover') state.flags.rateChanged = false;
        if (m === 'next-contribution') { state.flags.extraObserved = false; state.flags.dateChanged = false; }
        if (m === 'free') { state.applied = clone(draft); projection = calculated; }
      } catch (err) { state.valid = false; state.error = err.message; }
      patch();
    }
    function switchLever() {
      invalidate(); state.lever = field('lever').value;
      var base = ns.catalog.create('three-levers'); state.draft = base; state.applied = clone(base); projection = projectPair(base); prepared = projectPair(base); state.valid = true; state.error = ''; changed = false;
      ['A', 'B'].forEach(function (actor) {
        ['monthly', 'rate', 'horizon'].forEach(function (k) { var el = field(actor + '-' + k); el.value = k === 'monthly' ? 100 : k === 'rate' ? 6 : 240; el.disabled = (k === 'monthly' ? 'aporte' : k === 'rate' ? 'taxa' : 'prazo') !== state.lever; });
      }); patch();
    }
    function forecast() {
      if (state.mode !== 'guided' || !state.valid || !state.active || state.conflict) return;
      var choice = field('prediction').value;
      if (!choice) { state.forecastFeedback = 'Escolha uma previsão antes de aplicar o experimento.'; patch(); return; }
      pause(); state.applied = clone(state.draft); projection = projectPair(state.applied); state.month = 0;
      var expected;
      if (state.id === 'crossover') { var p = projection[state.actor.toLowerCase()]; var cross = p.firstCrossoverMonth; expected = cross === null ? 'never' : cross <= p.scenario.horizonMonths / 2 ? 'early' : 'late'; }
      else { var delta = projection.a.finalBalance - projection.b.finalBalance; expected = Math.abs(delta) <= 1e-8 * Math.max(1, projection.a.finalBalance, projection.b.finalBalance) ? 'equal' : delta > 0 ? 'A' : 'B'; }
      state.prediction = { choice: choice, correct: choice === expected, actor: state.actor };
      // Grade now against the private committed projection; reveal only after observation.
      state.forecastFeedback = 'Previsão registrada. Agora avance e compare com o que você imaginou.';
      state.reasonCorrect = false; state.reasonFeedback = ''; state.feedback = 'Experimento aplicado. Use +1 mês, +12 meses ou Executar.'; state.cohort = ''; state.traceOpen = false; state.without = false;
      field('reason').value = ''; patch();
    }
    function observe() {
      if (!state.prediction || !completeMonth()) return;
      var f = state.flags;
      if (state.id === 'early-start') { if (projection.a.scenario.annualRate > 0 && projection.b.scenario.annualRate > 0) f.positiveObserved = true; if (projection.a.scenario.annualRate === 0 && projection.b.scenario.annualRate === 0) f.zeroObserved = true; }
      if (state.id === 'equal-budget' && changed) f.calendarObserved = true;
      if (state.id === 'three-levers' && changed) f.levers[state.lever] = true;
      if (state.id === 'next-contribution') {
        f.extraObserved = true;
        var dates = ['a', 'b'].map(function (actor) { return state.applied[actor].contributions.find(function (c) { return /-extra$/.test(c.id); }).month; }).join(':');
        if (f.extraDates.indexOf(dates) < 0) f.extraDates.push(dates);
        f.dateChanged = changed && f.extraDates.length >= 2;
      }
      if (state.id === 'crossover' && crossChanged) f.rateChanged = true;
      state.forecastFeedback = state.prediction.correct ? 'Sua previsão corresponde ao resultado observado. Investigue a causa.' : 'O resultado difere da sua previsão. Revise sua hipótese e confirme uma nova previsão para tentar novamente.';
    }
    function setMonth(month) {
      if (!canAdvance()) return;
      state.month = Math.max(0, Math.min(maxMonth(), month)); observe(); patch();
    }
    function canAdvance() { return !state.destroyed && state.active && !state.conflict && state.valid && (state.mode === 'free' || !!state.prediction); }
    function play() {
      if (state.running) { pause(); state.feedback = 'Pausado. Use Continuar quando quiser.'; patch(); return; }
      if (!canAdvance()) return;
      if (motionPreference && motionPreference.matches) { state.feedback = 'Movimento reduzido: avance com os botões de mês ou pela linha do tempo.'; patch(); return; }
      if (document.hidden || state.month >= maxMonth()) return;
      state.running = true; state.continued = true; var token = ++generation; lastTick = 0;
      function tick(now) {
        if (state.destroyed || token !== generation || !state.running || !state.active || document.hidden) return;
        if (!lastTick || now - lastTick >= 70) { lastTick = now; state.month = Math.min(maxMonth(), state.month + 1); observe(); patch(); }
        if (state.month >= maxMonth()) { pause(); return; }
        frame = window.requestAnimationFrame(tick);
      }
      frame = window.requestAnimationFrame(tick); patch();
    }
    function conditions() {
      var f = state.flags; var missing = [];
      if (!state.prediction || !state.prediction.correct) missing.push('registrar uma previsão que corresponda ao resultado');
      if (!completeMonth()) missing.push('observar até o fim do prazo');
      if (state.id === 'early-start' && (!f.positiveObserved || !f.zeroObserved)) missing.push('observar uma tentativa com taxa positiva e outra com taxa zero');
      if (state.id === 'equal-budget' && !f.calendarObserved) missing.push('deslocar um calendário e observar');
      if (state.id === 'contribution-story' && (!f.inspect || !f.trace || !f.without)) missing.push('selecionar um aporte, abrir a fórmula e comparar sem ele');
      if (state.id === 'three-levers' && (!f.levers.prazo || !f.levers.taxa || !f.levers.aporte)) missing.push('observar mudanças separadas de prazo, taxa e aporte');
      if (state.id === 'next-contribution' && (!f.extraObserved || !f.dateChanged)) missing.push('mover o extra e observar seu impacto');
      if (state.id === 'crossover' && (!f.crossInspected || !f.rateChanged)) missing.push('investigar o cruzamento e observar depois de mudar a taxa');
      if (!state.reasonCorrect) missing.push('verificar uma explicação causal correta');
      return missing;
    }
    function neutralReason() {
      if (state.id === 'early-start') return projection.a.scenario.annualRate === 0 && projection.b.scenario.annualRate === 0 ? 'Sem rendimentos, calendários diferentes preservam o mesmo principal nominal.' : 'Com principal igual, o calendário determina quantos meses cada aporte rende.';
      if (state.id === 'equal-budget') return 'O mesmo orçamento rende conforme o tempo de cada aporte; calendários iguais produzem resultados iguais.';
      if (state.id === 'next-contribution') {
        if (!state.prediction || !completeMonth()) return 'O tempo de capitalização do extra determina seu impacto, medido contra o cenário original.';
        var monthA = state.applied.a.contributions.find(function (c) { return c.id === 'A-extra'; }).month;
        var monthB = state.applied.b.contributions.find(function (c) { return c.id === 'B-extra'; }).month;
        if (monthA === monthB) return 'Extras iguais no mesmo mês têm o mesmo tempo de capitalização e impactos iguais contra cenários originais iguais.';
        var earlier = monthA < monthB ? 'A' : 'B';
        return 'O extra do Gêmeo ' + earlier + ' entra antes (mês ' + Math.min(monthA, monthB) + ' contra ' + Math.max(monthA, monthB) + '), capitaliza por mais meses e tem maior impacto contra o original.';
      }
      return ns.catalog.get(state.id).reasonChoices.find(function (c) { return c.id === ns.catalog.get(state.id).correctReason; }).label;
    }
    function explanation() {
      if (state.id === 'early-start') return 'O principal de cada investidor continua em R$ 1.000. Com taxa positiva, quem aplica antes dispõe de mais meses de capitalização; no mesmo mês, os resultados coincidem. Com taxa zero, a diferença nominal desaparece. Confira o calendário de A e B desta tentativa.';
      if (state.id === 'equal-budget') return 'Os dois mantêm doze aportes de R$ 100. Quem antecipa o bloco ganha mais meses de capitalização; blocos no mesmo calendário coincidem. O resultado depende do calendário escolhido nesta tentativa.';
      if (state.id === 'next-contribution') return neutralReason() + ' O impacto absoluto é a diferença entre o saldo com o extra e o original; o percentual usa o saldo original como denominador. A participação divide pelo saldo com o extra, uma medida diferente.';
      return ns.catalog.get(state.id).explanation;
    }
    function finish(status) {
      if (state.destroyed || state.mode !== 'guided') return;
      if (status === 'demonstrated' && (conditions().length || !state.valid || state.conflict)) return;
      if (status === 'demonstrated' && state.helped) status = 'assisted';
      if (status === 'assisted' && !state.helped) return;
      var ranks = { skipped: 1, assisted: 2, demonstrated: 3 }; var previous = state.progress.missions[state.id];
      if (!previous || ranks[status] > ranks[previous]) state.progress.missions[state.id] = status;
      var index = ns.catalog.ids.indexOf(state.id); var next = ns.catalog.ids[index + 1];
      state.progress.currentMissionId = next || state.id; checkpoint();
      if (next) setup('guided', next, false); else { home(); state.feedback = 'Jornada registrada.'; }
      patchProgress();
    }
    function updateCohorts() {
      var p = projection[state.actor.toLowerCase()]; var select = field('cohort');
      var signature = state.actor + '|' + p.cohorts.map(function (c) { return c.id + ':' + c.month + ':' + c.principal; }).join('|');
      if (select.dataset.signature !== signature) {
        select.textContent = ''; select.dataset.signature = signature;
        var groups = {};
        p.cohorts.forEach(function (c) { var year = c.month === 0 ? 'Capital inicial' : 'Ano ' + Math.ceil(c.month / 12); if (!groups[year]) { var group = document.createElement('optgroup'); group.label = year; groups[year] = group; select.appendChild(group); } var option = document.createElement('option'); option.value = c.id; option.textContent = (c.month === 0 ? 'Inicial' : 'Mês ' + c.month) + ' · ' + money(c.principal); groups[year].appendChild(option); });
        }
      if (!p.cohorts.some(function (c) { return c.id === state.cohort; })) state.cohort = p.cohorts.length ? p.cohorts[0].id : '';
      select.value = state.cohort; select.disabled = !p.cohorts.length;
    }
    function points(snapshots, end, yMax, horizon, property) {
      return snapshots.filter(function (s) { return s.month <= end; }).map(function (s, i) { return (i ? 'L' : 'M') + (48 + s.month / horizon * 532).toFixed(2) + ',' + (225 - s[property || 'balance'] / yMax * 195).toFixed(2); }).join(' ');
    }
    function patchChart(withoutResult, inspection) {
      var horizon = maxMonth(); var end = state.mode === 'free' ? horizon : state.month;
      var all = []; ['a', 'b'].forEach(function (actor) { var p = projection[actor]; for (var i = 0; i <= end; i += 1) { all.push(p.snapshots[Math.min(i, p.scenario.horizonMonths)].balance); } });
      var yMax = Math.max.apply(null, all.concat([1]));
      out('chart-max', money(yMax)); out('chart-end', 'mês ' + horizon);
      ['A', 'B'].forEach(function (actor) {
        var p = projection[actor.toLowerCase()]; var arr = p.snapshots.slice();
        if (p.scenario.horizonMonths < end) arr.push({ month: end, balance: p.finalBalance });
        q('[data-chart-line="' + actor + '"]').setAttribute('d', points(arr, end, yMax, horizon));
        var current = p.snapshots[Math.min(state.month, p.scenario.horizonMonths)]; var label = q('[data-chart-marker="' + actor + '"]');
        label.textContent = actor; label.setAttribute('x', Math.min(562, 51 + state.month / horizon * 532)); label.setAttribute('y', Math.max(32, Math.min(220, 225 - current.balance / yMax * 195 + (actor === 'A' ? -5 : 14))));
      });
      var cohortPath = ''; var withoutPath = '';
      if (inspection) {
        var selected = projection[state.actor.toLowerCase()];
        var cohort = selected.cohorts.find(function (c) { return c.id === state.cohort; });
        var arr = [];
        for (var m = 0; m <= Math.min(end, selected.scenario.horizonMonths); m += 1) arr.push({ month: m, balance: m < cohort.month ? 0 : cohort.principal * Math.pow(1 + selected.monthlyRate, m - cohort.month) });
        cohortPath = points(arr, end, yMax, horizon);
        if (withoutResult) withoutPath = points(withoutResult.snapshots, end, yMax, horizon);
      }
      q('[data-chart-line="cohort"]').setAttribute('d', cohortPath); q('[data-chart-line="without"]').setAttribute('d', withoutPath);
    }
    function patchInspection(reveal) {
      updateCohorts(); var p = projection[state.actor.toLowerCase()]; var inspection = null; var alternative = null;
      if (state.cohort) {
        inspection = sim.inspect(p, state.cohort, Math.min(state.month, p.scenario.horizonMonths));
        var message = (inspection.active ? 'Aporte selecionado' : 'Aporte futuro') + ': principal ' + money(inspection.principal) + ' · valor atual ' + money(inspection.value) + ' · retornos ' + money(inspection.returns) + ' · participação atual ' + percent(inspection.share) + '.';
        message += reveal ? ' No fim do prazo: ' + money(inspection.projectedValue) + ' · participação ' + percent(inspection.projectedShare) + '.' : ' Após observar o prazo completo: valor e participação finais.';
        if (state.without) { alternative = sim.without(p, state.cohort); if (reveal) message += ' Sem este aporte: ' + money(alternative.finalBalance) + '; diferença ' + money(alternative.delta) + ' (' + percent(alternative.relative) + ').'; }
        out('inspection', message);
      } else out('inspection', 'Sem aportes neste cenário. Saldo zero; participação sem base.');
      action('trace').disabled = !inspection || (state.mode === 'guided' && !state.prediction);
      action('without').disabled = action('trace').disabled;
      action('trace').textContent = state.traceOpen ? 'Fechar fórmula mês a mês' : 'Abrir fórmula mês a mês'; action('trace').setAttribute('aria-expanded', String(state.traceOpen));
      action('without').setAttribute('aria-pressed', String(state.without));
      hide('[data-section="trace"]', !state.traceOpen || !inspection);
      if (state.traceOpen && inspection) {
        var body = q('[data-output="trace"] tbody'); var limit = state.mode === 'free' ? p.scenario.horizonMonths : state.month;
        var signature = state.actor + '|' + state.cohort + '|' + limit + '|' + p.scenario.annualRate + '|' + inspection.principal + '|' + inspection.month;
        if (body.dataset.signature !== signature) {
          body.dataset.signature = signature;
          body.innerHTML = sim.trace(p, state.cohort).filter(function (row) { return row.month <= limit; }).map(function (row) { return '<tr><th scope="row">' + row.month + '</th><td>' + row.multiplier.toLocaleString('pt-BR', { maximumFractionDigits: 8 }) + '</td><td>' + money(row.value) + '</td></tr>'; }).join('');
          if (!body.children.length) body.innerHTML = '<tr><td colspan="3">Aporte futuro: a capitalização começa no mês do depósito.</td></tr>';
        }
      }
      patchChart(alternative, inspection);
    }
    function patch() {
      if (state.destroyed) return;
      patchProgress();
      if (state.mode === 'home' || !projection || !field('month')) return;
      var reveal = state.mode === 'free' || completeMonth();
      field('month').max = maxMonth(); field('month').value = state.month; field('month').disabled = !canAdvance();
      out('timeline-label', 'Mês ' + state.month + ' de ' + maxMonth() + (state.mode === 'guided' && !state.prediction ? ' · Registre sua previsão para começar.' : ''));
      var feedback = state.feedback;
      // Final guidance replaces stale execution hints, never an action response or warning.
      var advanceHint = !feedback || feedback === 'Experimento aplicado. Use +1 mês, +12 meses ou Executar.' || feedback === 'Premissas atualizadas. Avance para observar.' || feedback === 'Pausado. Use Continuar quando quiser.';
      if (advanceHint && completeMonth() && canAdvance()) feedback = state.mode === 'free' ? 'Prazo observado. Investigue um aporte, compare os cenários ou restaure o exercício.' : 'Prazo observado. Investigue os aportes e verifique sua explicação; repita para testar outra hipótese.';
      out('validation', state.error); out('feedback', feedback); out('forecast', state.forecastFeedback); out('reason-feedback', state.reasonFeedback);
      ['A', 'B'].forEach(function (actor) {
        var p = projection[actor.toLowerCase()]; var s = p.snapshots[Math.min(state.month, p.scenario.horizonMonths)];
        out('balance-' + actor, money(s.balance)); out('contributed-' + actor, money(s.totalContributed)); out('pending-' + actor, money(s.pendingContributions)); out('returns-' + actor, money(s.cumulativeReturns));
        var ended = state.month > p.scenario.horizonMonths;
        out('interest-' + actor, ended ? money(0) + ' · prazo encerrado' : money(s.interestEarned));
        out('contribution-' + actor, ended ? money(0) + ' · prazo encerrado' : money(s.contribution));
        out('final-' + actor, reveal ? money(p.finalBalance) : 'Após observar o prazo completo');
        out('status-' + actor, state.month > p.scenario.horizonMonths ? 'prazo encerrado' : '');
        if (state.id === 'next-contribution' && state.mode === 'guided') { var base = sim.project(state.applied['baseline' + actor]); var delta = sim.difference(base, p); out('extra-' + actor, reveal ? 'Extra de ' + actor + ' contra o original: ' + money(delta.absolute) + ' (' + percent(delta.relative) + '). Principal adicional: ' + money(delta.contributed) + '.' : 'Impacto de ' + actor + ': observe até o fim do prazo.'); }
        if (state.id === 'crossover' || state.mode === 'free') {
          var cross = p.firstCrossoverMonth; var text;
          if (!p.scenario.contributions.some(function (c) { return c.amount > 0; })) text = 'Não se aplica sem aporte programado.';
          else if (cross !== null && (state.mode === 'free' || state.month >= cross)) text = 'Primeiro cruzamento no mês ' + cross + ': rendimento do período maior que aporte do período.';
          else text = reveal ? 'Não houve cruzamento neste prazo.' : 'Nenhum cruzamento observado até o mês ' + state.month + '.';
          out('crossover-' + actor, actor + ': ' + text);
        }
      });
      if (state.id === 'three-levers') {
        var totalA = projection.a.snapshots[projection.a.scenario.horizonMonths].totalContributed;
        var totalB = projection.b.snapshots[projection.b.scenario.horizonMonths].totalContributed;
        out('lever-note', 'Uma alavanca por tentativa. Um prazo maior também acrescenta meses de aportes programados.' + (reveal ? ' Diferença no total depositado (A − B): ' + money(totalA - totalB) + '.' : ' Compare o total depositado ao fim do prazo.'));
      }
      action('step-prev').disabled = !canAdvance() || state.month <= 0; action('step-next').disabled = !canAdvance() || completeMonth(); action('step-year').disabled = !canAdvance() || completeMonth();
      action('play').disabled = !canAdvance() || (!state.running && completeMonth()); action('play').textContent = state.running ? 'Pausar' : state.continued ? 'Continuar' : 'Executar';
      action('predict').disabled = !state.valid || !state.active || state.conflict;
      if (state.mode === 'guided') {
        var correctOption = Array.from(field('reason').options).find(function (o) { return o.value === ns.catalog.get(state.id).correctReason; }); if (correctOption) correctOption.textContent = neutralReason();
        var pending = conditions();
        out('requirements', pending.length ? (state.helped ? 'Para concluir a prática com explicação: ' : 'Para demonstrar: ') + pending.join('; ') + '.' : state.helped ? 'Prática observada e explicada com ajuda. Você pode concluir com explicação.' : 'Experimento observado e explicado. Você pode concluir a missão.');
        var completionText = state.helped ? 'Concluir com explicação' : 'Concluir missão';
        if (action('complete').textContent !== completionText) action('complete').textContent = completionText;
        action('complete').disabled = pending.length > 0 || !state.valid || !state.active || state.conflict;
        action('reason').disabled = !state.prediction || !completeMonth() || !state.valid;
        action('assisted').hidden = !state.helped;
        hide('[data-output="explanation"]', !state.helped); out('explanation', state.helped ? explanation() : '');
        var index = ns.catalog.ids.indexOf(state.id); action('previous').disabled = index === 0; action('next').disabled = index === ns.catalog.ids.length - 1;
      }
      patchInspection(reveal);
    }
    function onInput(event) {
      var t = event.target; if (state.destroyed || !state.active || !t.dataset.field) return;
      if (t.dataset.field === 'month') { setMonth(Number(t.value)); return; }
      if (/^[AB]-/.test(t.dataset.field)) edit(t);
    }
    function onChange(event) {
      if (state.destroyed || !state.active) return;
      var name = event.target.dataset.field;
      if (name === 'lever') switchLever();
      else if (name === 'actor') { var actor = event.target.value; if (state.id === 'crossover' && state.mode === 'guided') invalidate(); state.actor = actor; state.cohort = ''; state.traceOpen = false; state.without = false; patch(); }
      else if (name === 'cohort') { state.cohort = event.target.value; if (state.prediction) state.flags.inspect = true; state.traceOpen = false; state.without = false; patch(); }
    }
    function onClick(event) {
      var target = event.target.closest('button'); if (!target || !root.contains(target) || target.disabled || state.destroyed || !state.active) return;
      if (target.dataset.mission) { setup('guided', target.dataset.mission, true); return; }
      var name = target.dataset.action;
      if (name === 'start') setup('guided', ns.catalog.ids[0], true);
      else if (name === 'continue') setup('guided', state.progress.currentMissionId, false);
      else if (name === 'free') setup('free');
      else if (name === 'journey') home();
      else if (name === 'restore' || name === 'repeat') setup(state.mode, state.id, false);
      else if (name === 'predict') forecast();
      else if (name === 'step-prev') { pause(); setMonth(state.month - 1); }
      else if (name === 'step-next') { pause(); setMonth(state.month + 1); }
      else if (name === 'step-year') { pause(); setMonth(state.month + 12); }
      else if (name === 'play') play();
      else if (name === 'zero' || name === 'positive') {
        invalidate();
        try {
          var draft = singleDepositPair();
          draft.a.annualRate = draft.b.annualRate = name === 'zero' ? 0 : .06;
          var nextProjection = projectPair(draft);
          state.draft = draft; state.applied = clone(draft); projection = prepared = nextProjection;
          state.valid = true; state.error = '';
          state.feedback = name === 'zero' ? 'Taxa zero nos dois investidores. Faça uma nova previsão com o mesmo calendário.' : 'Taxa de 6% ao ano nos dois. Faça uma nova previsão.';
        } catch (err) { state.valid = false; state.error = err.message; }
        patch();
      }
      else if (name === 'trace') { state.traceOpen = !state.traceOpen; if (state.prediction && completeMonth() && state.traceOpen) { state.flags.trace = true; } patch(); }
      else if (name === 'without') { state.without = !state.without; if (state.prediction && completeMonth() && state.without) { state.flags.without = true; } patch(); }
      else if (name === 'cross') { if (state.prediction && (completeMonth() || (projection[state.actor.toLowerCase()].firstCrossoverMonth !== null && state.month >= projection[state.actor.toLowerCase()].firstCrossoverMonth))) { state.flags.crossInspected = true; state.feedback = 'Compare rendimento e aporte do mesmo mês. O marco depende das premissas e não implica independência financeira.'; } else state.feedback = 'Avance até o marco ou até o fim do prazo para investigar sua ausência.'; patch(); }
      else if (name === 'reason') { if (!state.prediction || !completeMonth() || !state.valid) return; state.reasonCorrect = field('reason').value === ns.catalog.get(state.id).correctReason; state.reasonFeedback = state.reasonCorrect ? 'Relação causal correta. ' + (state.id === 'next-contribution' ? explanation() : neutralReason()) : 'Essa explicação não corresponde ao experimento. Compare principal, calendário e rendimentos e tente novamente.'; patch(); }
      else if (name === 'help') { pause(); state.helped = true; patch(); }
      else if (name === 'complete') finish('demonstrated');
      else if (name === 'assisted') finish('assisted');
      else if (name === 'skip') finish('skipped');
      else if (name === 'previous' || name === 'next') { var i = ns.catalog.ids.indexOf(state.id) + (name === 'next' ? 1 : -1); if (ns.catalog.ids[i]) setup('guided', ns.catalog.ids[i], true); }
      else if (name === 'restart') { pause(); hide('[data-section="restart"]', false); action('confirm-restart').focus(); }
      else if (name === 'cancel-restart') { hide('[data-section="restart"]', true); action('restart').focus(); }
      else if (name === 'confirm-restart') {
        pause(); var result = ns.progress.restart({ storage: store, expectedRaw: raw });
        if (result.ok || result.raw === undefined) { state.progress = clone(result.value); raw = result.raw; state.conflict = false; state.blocked = result.blocked; state.storageMessage = result.error || ''; hide('[data-section="restart"]', true); setup('guided', ns.catalog.ids[0], false); }
        else { state.storageMessage = result.error; state.conflict = true; patchProgress(); }
      } else if (name === 'reload') {
        pause(); saved = ns.progress.read(store); raw = saved.raw; state.progress = clone(saved.value); state.conflict = false; state.blocked = saved.blocked; state.storageMessage = saved.error || ''; home();
      }
    }
    function onVisibility() { if (document.hidden) { pause(); state.feedback = 'Pausado ao ocultar a página. Use Continuar para retomar.'; patch(); } }
    function onMotion(event) { if (event.matches) { pause(); state.feedback = 'Movimento reduzido: avance com os botões de mês ou pela linha do tempo.'; patch(); } }
    function onStorage(event) { if (event.key === ns.progress.key || event.key === null) { invalidate(); state.conflict = true; state.storageMessage = 'O progresso mudou em outra aba. Recarregue o progresso para retomar as gravações.'; patch(); } }
    function activate() { if (state.destroyed) return controller; state.active = true; root.hidden = false; pause(); patch(); return controller; }
    function deactivate() { if (state.destroyed) return; pause(); state.active = false; root.hidden = true; }
    function destroy() {
      if (state.destroyed) return;
      pause(); state.destroyed = true; state.active = false;
      root.removeEventListener('click', onClick); root.removeEventListener('input', onInput); root.removeEventListener('change', onChange);
      document.removeEventListener('visibilitychange', onVisibility); window.removeEventListener('storage', onStorage);
      if (motionPreference) { if (motionPreference.removeEventListener) motionPreference.removeEventListener('change', onMotion); else if (motionPreference.removeListener) motionPreference.removeListener(onMotion); }
      instances.delete(controller); delete root.__timeTwinsController; if (host.__timeTwinsController === controller) delete host.__timeTwinsController;
      root.replaceChildren(); root.remove(); state.progress = null; state.prediction = null; state.flags = {}; state.cohort = ''; projection = null; prepared = null; freeSettings = null; state.draft = null; state.applied = null; store = null;
    }
    function snapshot() { return clone(state); }
    var controller = { activate: activate, pause: pause, deactivate: deactivate, destroy: destroy, snapshot: snapshot };
    root.__timeTwinsController = controller; host.__timeTwinsController = controller; instances.add(controller);
    root.addEventListener('click', onClick); root.addEventListener('input', onInput); root.addEventListener('change', onChange); document.addEventListener('visibilitychange', onVisibility); window.addEventListener('storage', onStorage);
    if (motionPreference) { if (motionPreference.addEventListener) motionPreference.addEventListener('change', onMotion); else if (motionPreference.addListener) motionPreference.addListener(onMotion); }
    patchProgress(); return controller;
  }
  ns.mount = mount;
  ns.activate = function (host) { return mount(host).activate(); };
  ns.deactivate = function (host) { var controller = host && host.__timeTwinsController; if (controller) controller.deactivate(); };
  ns.dispose = function () { Array.from(instances).forEach(function (controller) { controller.destroy(); }); };
})(window);
