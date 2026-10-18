/* Session-only visual laboratory: owns DOM and animation, never financial state. */
(function (global) {
  'use strict';
  var ns = global.JPWCapitalCurrents = global.JPWCapitalCurrents || {}, instances = new Set();
  function mount(host) {
    if (!host) throw new TypeError('A host is required');
    if (host.__capitalCurrentsController && !host.__capitalCurrentsController.snapshot().destroyed) return host.__capitalCurrentsController;
    var wrapper = document.createElement('div'); wrapper.innerHTML = ns.view.panelHTML(); var root = wrapper.firstElementChild; host.appendChild(root);
    var canvas = root.querySelector('canvas'), renderer = ns.renderer.create(canvas), active = false, running = false, destroyed = false, frame = null, last = null, accumulator = 0;
    var state = { q: 0, p: 0, t: 0 }, params = Object.assign({}, ns.engine.DEFAULTS), tick = 0, exited = false, trail = [Object.assign({}, state)], particles = [], seed = 0;
    var layers = { vectors: true, streamlines: true, particles: true, trail: true };
    var gesture = null, pointers = new Set();
    var renderedLessonId = null;
    var loaded = ns.progress.load(), progress = loaded.value, progressRaw = loaded.raw, storageMode = loaded.mode, conflict = false;
    var learning = { id: null, open: false, suspended: false, eligible: false, evidence: {}, comparison: null, resetPending: false };
    function copy(value) { return JSON.parse(JSON.stringify(value)); }
    function statusLabel(status) { return ({seen: 'Orientação vista', practiced: 'Prática realizada', skipped: 'Etapa pulada'})[status] || 'Ainda não visitada'; }
    function blocked() { return conflict || destroyed || foreignDialog(); }
    function observing() { return learning.open && learning.id && !learning.suspended && !blocked() && active && !document.hidden; }
    function clearEvidence() { learning.eligible = false; learning.evidence = {}; learning.comparison = null; }
    function suspendLearning() { if (learning.open && !learning.suspended) { learning.suspended = true; renderLearning(); } }
    function persist(status) {
      if (!observing() || storageMode === 'incompatible') return;
      var next = ns.progress.mark(progress, learning.id, status), result = ns.progress.save(next, undefined, progressRaw);
      if (result.ok) { progress = next; progressRaw = result.raw; storageMode = 'ok'; }
      else if (result.mode === 'temporary') { progress = next; storageMode = 'temporary'; }
      else if (result.mode === 'incompatible') { storageMode = 'incompatible'; }
      else { conflict = true; storageMode = 'conflict'; pause(); learning.suspended = true; clearEvidence(); }
      renderLearning(); patch();
    }
    function openLesson(id) {
      if (!ns.catalog.get(id) || blocked()) return;
      pause(); learning.id = id; learning.open = true; learning.suspended = false; learning.resetPending = false; clearEvidence(); renderLearning();
    }
    function listHTML(kind) {
      return ns.catalog.items.filter(function(item) { return !kind || item.kind === kind; }).map(function(item) {
        return '<button type="button" data-action="lesson" data-lesson="' + item.id + '">' + item.title + ' · ' + statusLabel(progress.steps[item.id]) + '</button>';
      }).join('');
    }
    function comparisonHTML(result) {
      if (!result) return '';
      function point(s) { return ((s.q + 1) * 150 + 35).toFixed(2) + ',' + ((6 - s.p) * 20 + 15).toFixed(2); }
      var a = result.a[result.a.length - 1], b = result.b[result.b.length - 1];
      return '<p>Comparação do modelo, se estas condições forem mantidas. Estado inicial comum: q = ' + decimal(result.initial.q) + ', p = ' + decimal(result.initial.p) + ', t = ' + decimal(result.initial.t) + ' s. Duração: ' + decimal(result.duration) + ' s.</p>' +
        '<p>A (linha contínua, círculo): ' + result.labelA + '; profundidade ' + result.paramsA.depth + ', perfil ' + (result.paramsA.profile === 'band' ? 'faixa rasa' : 'uniforme') + '.<br>B (linha tracejada, quadrado): ' + result.labelB + '; profundidade ' + result.paramsB.depth + ', perfil ' + (result.paramsB.profile === 'band' ? 'faixa rasa' : 'uniforme') + '. τ = 1 s; κ = 2 em ambos.</p>' +
        '<svg viewBox="0 0 370 290" role="img" aria-label="Comparação com eixos comuns q menos um a um e p menos seis a seis"><rect x="35" y="15" width="300" height="240" fill="none" stroke="currentColor"/><path d="M35 135H335 M185 15V255" stroke="currentColor" opacity=".3"/><text x="35" y="275">q −1</text><text x="300" y="275">q +1</text><text x="0" y="25">p +6</text><text x="0" y="253">p −6</text><polyline data-series="a" points="' + result.a.map(point).join(' ') + '" fill="none" stroke="#1683a2" stroke-width="3"/><polyline data-series="b" points="' + result.b.map(point).join(' ') + '" fill="none" stroke="#bc6617" stroke-width="3" stroke-dasharray="7 4"/><circle cx="' + point(a).split(',')[0] + '" cy="' + point(a).split(',')[1] + '" r="5" fill="#1683a2"/><rect x="' + (Number(point(b).split(',')[0])-4) + '" y="' + (Number(point(b).split(',')[1])-4) + '" width="8" height="8" fill="#bc6617"/></svg>' +
        '<p data-comparison-result>A: q = ' + decimal(a.q,6) + ', p = ' + decimal(a.p,6) + '. B: q = ' + decimal(b.q,6) + ', p = ' + decimal(b.p,6) + '. Diferença B − A: q = ' + decimal(b.q-a.q,6) + ', p = ' + decimal(b.p-a.p,6) + '. Resultado deste modelo; não é previsão de mercado.</p>';
    }
    function renderLearning() {
      if (destroyed) return;
      var storageText = conflict ? 'Progresso em conflito. Aprendizado e simulação pausados. Releia para continuar.' : storageMode === 'temporary' ? 'Somente nesta sessão. O navegador não confirmou armazenamento.' : storageMode === 'incompatible' ? 'Progresso incompatível preservado. Recomece explicitamente para salvar novas etapas.' : 'Somente etapas de aprendizado são salvas neste navegador.';
      q('[data-learning-storage]').textContent = storageText;
      var panel = q('[data-learning-panel]'), focused = panel.contains(document.activeElement) ? document.activeElement : null, focusedAction = focused && focused.dataset.action, focusedLesson = focused && focused.dataset.lesson; if (panel.hidden !== !learning.open) panel.hidden = !learning.open;
      var cue = q('[data-learning-cue]'), cueItem = ns.catalog.get(learning.id); if (cue.hidden !== !learning.open) cue.hidden = !learning.open; cue.textContent = learning.open ? (cueItem ? (learning.suspended ? 'Aprendizado pausado · ' : '') + cueItem.title + ': ' + cueItem.instruction : 'Descobertas abertas abaixo do campo. Escolha uma comparação opcional.') : '';
      if (!learning.open) { renderedLessonId = null; if (focused) q('[data-action="learn"]').focus(); return; }
      var item = ns.catalog.get(learning.id), disabled = conflict || storageMode === 'incompatible' || learning.suspended ? ' disabled' : '';
      var html = '<div class="capital-field-learning-actions"><button type="button" data-action="free">Explorar livremente / Fechar</button><button type="button" data-action="reread">Reler progresso</button><button type="button" data-action="restart-progress">Recomeçar progresso</button></div>';
      if (learning.resetPending) html += '<p>Apagar somente as etapas de aprendizado? O cenário atual será preservado.</p><button type="button" data-action="confirm-restart">Confirmar reinício do progresso</button><button type="button" data-action="cancel-restart">Cancelar</button>';
      if (item) {
        html += '<p class="capital-field-note">Prática realizada registra uma atividade observada, sem avaliar sua compreensão.</p>';
        html += '<h4 tabindex="-1">' + item.title + '</h4><p><strong>' + statusLabel(progress.steps[item.id]) + '</strong></p><p>Objetivo: ' + item.goal + '</p><p>' + item.explanation + '</p><p>Faça: ' + item.instruction + '</p><p>Observe: ' + item.expected + '</p>';
        if (learning.suspended) html += '<p>Aprendizado pausado. Retome por escolha explícita.</p><button type="button" data-action="resume-learning"' + (conflict ? ' disabled' : '') + '>Retomar aprendizado</button>';
        html += '<div class="capital-field-learning-actions"><button type="button" data-action="seen"' + disabled + '>Entendi a orientação</button><button type="button" data-action="practice"' + (disabled || (!learning.eligible ? ' disabled' : '')) + '>Concluir prática · observei o resultado</button>';
        if (item.kind === 'discovery') html += '<button type="button" data-action="compare"' + disabled + '>Comparar cenários</button>';
        if (item.id === 'intro-pressure') html += '<button type="button" data-action="prepare"' + disabled + '>Preparar exemplo</button>';
        html += '<button type="button" data-action="previous">Voltar</button><button type="button" data-action="next">Próximo</button><button type="button" data-action="skip"' + disabled + '>Pular</button><button type="button" data-action="pause-learning">Pausar aprendizado</button></div>';
        html += '<p data-learning-result>' + (learning.evidence.result || '') + '</p>';
        html += comparisonHTML(learning.comparison);
      } else html += '<h4 tabindex="-1">Descobertas opcionais</h4><p>Escolha uma comparação. As condições do campo atual serão preservadas.</p>';
      html += '<div class="capital-field-learning-list">' + listHTML(item ? null : 'discovery') + '</div>';
      panel.innerHTML = html;
      if (focused) {
        var target;
        if (learning.resetPending && focusedAction === 'restart-progress') target = panel.querySelector('[data-action="confirm-restart"]');
        else if (focusedAction === 'confirm-restart' || focusedAction === 'cancel-restart') target = panel.querySelector('[data-action="restart-progress"]');
        else if (renderedLessonId !== learning.id) target = panel.querySelector('h4');
        else if (focusedAction === 'lesson' && focusedLesson) target = panel.querySelector('[data-lesson="' + focusedLesson + '"]');
        else if (focusedAction) target = panel.querySelector('[data-action="' + focusedAction + '"]');
        if (!target || target.disabled) target = panel.querySelector('h4') || panel.querySelector('[data-action="reread"]');
        if (target) target.focus({preventScroll:true});
      }
      renderedLessonId = learning.id;
    }
    function observedAdvance(before) {
      if (!observing() || learning.eligible || state.t <= before.t) return;
      var e = learning.evidence;
      if (learning.id === 'intro-field' && e.selected) {
        learning.eligible = true; e.result = 'Antes: q = ' + decimal(before.q) + ', p = ' + decimal(before.p) + ', t = ' + decimal(before.t) + ' s. Depois: q = ' + decimal(state.q) + ', p = ' + decimal(state.p) + ', t = ' + decimal(state.t) + ' s. Movimento ou ausência de movimento observado.';
      }
      if (learning.id === 'intro-pressure') {
        if (params.u !== 0 && state.q !== 0) e.applied = true;
        if (e.released && params.u === 0 && Math.abs(state.q) < Math.abs(e.released.q) && (state.p-e.released.p)*e.released.q > 0) {
          learning.eligible = true; e.result = 'Após retirar u: q passou de ' + decimal(e.released.q) + ' para ' + decimal(state.q) + '; p passou de ' + decimal(e.released.p) + ' para ' + decimal(state.p) + '. A pressão diminuiu e o preço continuou na direção observada.';
        }
      }
      if (learning.eligible) { var resultNode = q('[data-learning-result]'); if (resultNode) resultNode.textContent = learning.evidence.result; var completion = q('[data-action="practice"]'); if (completion && storageMode !== 'incompatible') completion.disabled = false; }
    }
    function onStorage(event) {
      if (destroyed || (event.key !== ns.progress.KEY && event.key !== null)) return;
      conflict = true; storageMode = 'conflict'; pause(); learning.suspended = true; learning.resetPending = false; clearEvidence(); renderLearning(); patch();
    }
    function learningAction(action, button) {
      if (action === 'reread') {
        pause(); var fresh = ns.progress.load(); progress = fresh.value; progressRaw = fresh.raw; storageMode = fresh.mode; conflict = false; learning.resetPending = false; clearEvidence(); learning.suspended = false; renderLearning(); patch(); return true;
      }
      if (action === 'free') { pause(); learning.open = false; learning.suspended = true; renderLearning(); return true; }
      if (action === 'restart-progress' && !conflict) { pause(); learning.resetPending = true; renderLearning(); return true; }
      if (action === 'cancel-restart') { learning.resetPending = false; renderLearning(); return true; }
      if (action === 'confirm-restart' && learning.resetPending && !conflict) {
        pause(); var result = ns.progress.restart(undefined, progressRaw); learning.resetPending = false;
        if (result.mode === 'ok' || result.mode === 'temporary') { progress = result.value; if (result.mode === 'ok') progressRaw = result.raw; storageMode = result.mode; clearEvidence(); }
        else { conflict = true; storageMode = 'conflict'; learning.suspended = true; clearEvidence(); }
        renderLearning(); patch(); return true;
      }
      if (blocked()) return false;
      if (action === 'learn') { openLesson('intro-field'); return true; }
      if (action === 'continue-learning') { openLesson((ns.catalog.items.find(function(item) { return !progress.steps[item.id]; }) || ns.catalog.items[0]).id); return true; }
      if (action === 'discoveries') { pause(); learning.open = true; learning.id = null; learning.suspended = false; clearEvidence(); renderLearning(); return true; }
      if (action === 'lesson') { openLesson(button.dataset.lesson); return true; }
      if (action === 'pause-learning') { pause(); suspendLearning(); return true; }
      if (action === 'resume-learning') { learning.suspended = false; renderLearning(); return true; }
      if (!learning.open || !learning.id) return false;
      var index = ns.catalog.items.findIndex(function(item) { return item.id === learning.id; });
      if (action === 'previous' || action === 'next') { openLesson(ns.catalog.items[Math.max(0,Math.min(ns.catalog.items.length-1,index+(action === 'next' ? 1 : -1)))].id); return true; }
      if (!observing()) return false;
      if (action === 'seen') { persist('seen'); return true; }
      if (action === 'practice') { if (learning.eligible) persist('practiced'); return true; }
      if (action === 'skip') { persist('skipped'); if (!conflict) openLesson(ns.catalog.items[Math.min(index+1,ns.catalog.items.length-1)].id); return true; }
      if (action === 'compare' && ns.catalog.get(learning.id).kind === 'discovery') { pause(); clearEvidence(); learning.comparison = ns.catalog.experiment(learning.id); learning.eligible = true; renderLearning(); return true; }
      if (action === 'prepare' && learning.id === 'intro-pressure') { params.u = .4; field('u').value = '.4'; position({q:0,p:0,t:0}, false); return true; }
      return false;
    }
    function clearGesture() { gesture = null; pointers.clear(); }
    function q(selector) { return root.querySelector(selector); }
    function field(name) { return q('[data-field="' + name + '"]'); }
    function out(name, text) { q('[data-output="' + name + '"]').textContent = text; }
    function decimal(value, places) { return value.toFixed(places === undefined ? 3 : places).replace('.', ','); }
    function notice(text) { if (!destroyed) out('status', text); }
    function seedParticle() {
      var index = seed++; // Deterministic examples; refreshed only after exiting, never bounced or wrapped.
      return { q: -.97 + ((index * .61803398875 + .13) % 1) * 1.94, p: -5.9 + ((index * .41421356237 + .37) % 1) * 11.8, t: 0 };
    }
    function refreshParticles() { seed = 0; particles = []; var count = canvas.getBoundingClientRect().width < 500 ? 100 : 180; for (var i = 0; i < count; i++) particles.push(seedParticle()); }
    function patch() {
      if (destroyed) return;
      var f = ns.engine.fieldAt(state, params); out('time', decimal(state.t, 2) + ' s'); out('u', (params.u > 0 ? '+' : '') + decimal(params.u, 2));
      out('q', decimal(state.q)); out('p', decimal(state.p)); out('depth', decimal(f.depth)); out('dq', decimal(f.dq)); out('dp', decimal(f.dp));
      q('[data-action="play"]').textContent = running ? 'Pausar' : tick ? 'Continuar' : 'Iniciar';
      q('[data-action="play"]').disabled = exited || conflict; q('[data-action="step"]').disabled = exited || conflict;
      renderer.draw({ state: state, params: params, layers: layers, particles: particles, trail: trail });
    }
    function pause(message) {
      if (destroyed) return;
      clearGesture(); running = false; if (frame !== null) global.cancelAnimationFrame(frame); frame = null; last = null; accumulator = 0;
      if (message) notice(message); q('[data-action="play"]').textContent = tick ? 'Continuar' : 'Iniciar';
    }
    function foreignDialog() {
      return Array.from(document.querySelectorAll('dialog[open],[role="dialog"]')).some(function (dialog) { return !root.contains(dialog) && !dialog.closest('[hidden],[inert],[aria-hidden="true"]') && dialog.getClientRects().length > 0 && global.getComputedStyle(dialog).visibility !== 'hidden'; });
    }
    function inside(s) { return s.q >= -1 && s.q <= 1 && s.p >= -6 && s.p <= 6; }
    function advance(count) {
      var beforeAdvance = copy(state);
      for (var i = 0; i < count && !exited; i++) {
        state = ns.engine.advance(state, params, ns.engine.DT); tick++;
        trail.push(Object.assign({}, state)); if (trail.length > 1800) trail.shift();
        particles = particles.map(function (s) { var next = ns.engine.advance(s, params, ns.engine.DT); return inside(next) ? next : seedParticle(); });
        if (!inside(state)) { exited = true; pause('O cenário saiu da janela. Trajetória encerrada; escolha outro ponto ou restaure o laboratório.'); }
      }
      observedAdvance(beforeAdvance);
    }
    function animate(now) {
      frame = null; if (!active || destroyed) return;
      if (document.hidden || foreignDialog()) { suspendLearning(); pause('Pausado ao ocultar o campo. Retome explicitamente.'); return; }
      if (last !== null) accumulator += Math.max(0, Math.min(.1, (now - last) / 1000)); last = now;
      var count = Math.min(6, Math.floor((accumulator + 1e-12) / ns.engine.DT)); accumulator -= count * ns.engine.DT;
      if (count) { advance(count); patch(); }
      if (running) frame = global.requestAnimationFrame(animate);
    }
    function play() {
      if (destroyed || !active || exited || conflict || document.hidden || foreignDialog()) return;
      if (running) { pause('Pausado. O cenário e seu caminho foram preservados.'); return; }
      running = true; last = null; accumulator = 0; notice(global.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'Executando por sua escolha. Você também pode avançar em passos de 0,25 s.' : 'Executando. Ajuste a pressão e observe como o cenário responde.');
      patch(); frame = global.requestAnimationFrame(animate);
    }
    function position(next, selected) {
      clearEvidence(); if (selected !== false && observing() && learning.id === 'intro-field') learning.evidence.selected = true; renderLearning();
      pause(); state = next; tick = 0; exited = false; trail = [Object.assign({}, state)]; refreshParticles(); field('q').value = String(Number(state.q.toFixed(4))); field('p').value = String(Number(state.p.toFixed(4))); out('error', ''); notice('Novo cenário escolhido. Relógio e caminho reiniciados em 0 s; controles preservados.'); patch();
    }
    function onClick(event) {
      if (!active || destroyed || document.hidden || foreignDialog()) return; var button = event.target.closest('[data-action]'); if (!button || !root.contains(button)) return;
      var action = button.dataset.action;
      if (learningAction(action, button)) return;
      if (conflict || foreignDialog() || document.hidden) return;
      if (action === 'play') play();
      else if (action === 'step' && !exited) { pause(); advance(15); if (!exited) notice('Avanço de 0,25 s observado. Campo pausado.'); patch(); }
      else if (action === 'release') { var applied = observing() && learning.id === 'intro-pressure' && learning.evidence.applied && params.u !== 0; clearEvidence(); if (applied) learning.evidence.released = copy(state); renderLearning(); params.u = 0; field('u').value = '0'; notice('Pressão aplicada retirada. O cenário e o relógio continuam; a pressão efetiva decai gradualmente.'); patch(); }
      else if (action === 'reset') {
        params = Object.assign({}, ns.engine.DEFAULTS); field('u').value = String(params.u); field('depth').value = String(params.depth); field('band').checked = false; position({ q: 0, p: 0, t: 0 }, false); notice('Laboratório restaurado aos controles iniciais. Pausado em 0 s.');
      } else if (action === 'position') {
        var qRaw = field('q').value.trim(), pRaw = field('p').value.trim(), qValue = Number(qRaw), pValue = Number(pRaw);
        if (!qRaw || !pRaw || !Number.isFinite(qValue) || !Number.isFinite(pValue) || qValue < -1 || qValue > 1 || pValue < -6 || pValue > 6) { clearEvidence(); renderLearning(); out('error', 'Preencha q entre −1 e 1 e p entre −6 e 6. O último cenário foi preservado.'); return; }
        position({ q: qValue, p: pValue, t: 0 });
      }
    }
    function onInput(event) {
      if (!active || destroyed || conflict || foreignDialog() || event.target.dataset.field !== 'u') return;
      var value = Number(event.target.value); if (!Number.isFinite(value) || value < -1 || value > 1) return; clearEvidence(); renderLearning(); params.u = value; patch();
    }
    function onChange(event) {
      if (!active || destroyed || conflict || foreignDialog()) return; var input = event.target;
      if (input.dataset.layer) { layers[input.dataset.layer] = input.checked; patch(); }
      else if (input.dataset.field === 'depth') {
        var depth = Number(input.value); if ([.5, 1, 2].indexOf(depth) < 0) return;
        var before = ns.engine.fieldAt(state, params); clearEvidence(); params.depth = depth; var after = ns.engine.fieldAt(state, params);
        if (observing() && learning.id === 'intro-depth' && state.q !== 0 && before.dp !== after.dp) { learning.eligible = true; learning.evidence.result = 'Mesmo q = ' + decimal(state.q) + ', p = ' + decimal(state.p) + ', t = ' + decimal(state.t) + ' s: dp/dt passou de ' + decimal(before.dp) + ' para ' + decimal(after.dp) + ' pontos/s.'; } renderLearning();
        notice(state.q === 0 ? 'Com q = 0, não há movimento do preço: profundidade sozinha não move o preço. Cenário, relógio e caminho preservados.' : 'No mesmo cenário, com q = ' + decimal(state.q) + ', dp/dt passou de ' + decimal(before.dp) + ' para ' + decimal(after.dp) + ' pontos/s neste modelo ilustrativo. Cenário, relógio e caminho preservados.'); patch();
      }
      else if (input.dataset.field === 'band') { clearEvidence(); renderLearning(); params.profile = input.checked ? 'band' : 'uniform'; notice('Perfil de profundidade alterado; cenário e caminho preservados.'); patch(); }
    }
    function onPointerDown(event) {
      if (!active || destroyed || conflict || foreignDialog() || (event.target !== canvas && pointers.size === 0)) return;
      pointers.add(event.pointerId);
      if (event.target !== canvas || !event.isPrimary || event.button !== 0 || pointers.size !== 1) { gesture = null; return; }
      gesture = { id: event.pointerId, x: event.clientX, y: event.clientY };
    }
    function onPointerMove(event) {
      if (gesture && gesture.id === event.pointerId && Math.hypot(event.clientX - gesture.x, event.clientY - gesture.y) > 8) gesture = null;
    }
    function onPointerCancel(event) { gesture = null; pointers.delete(event.pointerId); }
    function onPointerUp(event) {
      var tap = gesture; gesture = null; pointers.delete(event.pointerId);
      if (!active || destroyed || conflict || foreignDialog() || !tap || tap.id !== event.pointerId || !event.isPrimary || event.button !== 0 || pointers.size || Math.hypot(event.clientX - tap.x, event.clientY - tap.y) > 8) return;
      var bounds = canvas.getBoundingClientRect(), next = renderer.pick((event.clientX - bounds.left) * canvas.clientWidth / bounds.width, (event.clientY - bounds.top) * canvas.clientHeight / bounds.height); if (next) position(next);
    }
    function onKey(event) { if (event.key === 'Escape' && active) { suspendLearning(); pause('Pausado pela tecla Escape.'); } }
    function onBlur() { if (active) { suspendLearning(); pause('Pausado ao sair da janela. Retome explicitamente.'); } }
    function onVisibility() { if (document.hidden && active) { suspendLearning(); pause('Pausado ao ocultar a página. Retome explicitamente.'); } }
    function onResize() { if (active && !destroyed) { renderer.resize(); patch(); } }
    var resizeObserver = typeof ResizeObserver === 'function' ? new ResizeObserver(onResize) : null;
    var dialogObserver = new MutationObserver(function (records) {
      if (!active || destroyed) return;
      var relevant = records.some(function (r) { return r.type === 'attributes' || Array.from(r.addedNodes).some(function (node) { return node.nodeType === 1 && (node.matches('dialog,[role="dialog"]') || node.querySelector('dialog,[role="dialog"]')); }); });
      if (relevant && foreignDialog()) { suspendLearning(); pause('Pausado enquanto outra janela está aberta. Retome explicitamente.'); }
    });
    function activate() { if (destroyed || active) return controller; active = true; root.hidden = false; renderer.resize(); patch(); return controller; }
    function deactivate() { if (destroyed) return; suspendLearning(); pause('Campo pausado ao sair. Retome explicitamente.'); active = false; root.hidden = true; }
    function snapshot() {
      return JSON.parse(JSON.stringify({ active: active, running: running, destroyed: destroyed, loopScheduled: frame !== null, tick: tick, time: state.t, state: state, params: params, layers: layers, exited: exited, particleCount: particles.length, trailCount: trail.length, field: renderer.snapshot(), learning: { id: learning.id, open: learning.open, suspended: learning.suspended, eligible: learning.eligible, progress: progress, storageMode: storageMode, conflict: conflict, evidence: learning.evidence, comparison: learning.comparison } }));
    }
    function destroy() {
      if (destroyed) return; pause(); destroyed = true; active = false;
      root.removeEventListener('click', onClick); root.removeEventListener('input', onInput); root.removeEventListener('change', onChange); global.removeEventListener('pointerdown', onPointerDown); global.removeEventListener('pointermove', onPointerMove); global.removeEventListener('pointerup', onPointerUp); global.removeEventListener('pointercancel', onPointerCancel); canvas.removeEventListener('lostpointercapture', onPointerCancel);
      document.removeEventListener('keydown', onKey); document.removeEventListener('visibilitychange', onVisibility); global.removeEventListener('blur', onBlur); global.removeEventListener('resize', onResize); global.removeEventListener('storage', onStorage);
      if (resizeObserver) resizeObserver.disconnect(); dialogObserver.disconnect(); renderer.destroy(); instances.delete(controller); delete host.__capitalCurrentsController; delete root.__capitalCurrentsController; root.remove(); particles = []; trail = [];
    }
    var controller = { activate: activate, deactivate: deactivate, pause: pause, destroy: destroy, snapshot: snapshot };
    host.__capitalCurrentsController = root.__capitalCurrentsController = controller; instances.add(controller);
    root.addEventListener('click', onClick); root.addEventListener('input', onInput); root.addEventListener('change', onChange); global.addEventListener('pointerdown', onPointerDown); global.addEventListener('pointermove', onPointerMove); global.addEventListener('pointerup', onPointerUp); global.addEventListener('pointercancel', onPointerCancel); canvas.addEventListener('lostpointercapture', onPointerCancel);
    document.addEventListener('keydown', onKey); document.addEventListener('visibilitychange', onVisibility); global.addEventListener('blur', onBlur); global.addEventListener('resize', onResize); global.addEventListener('storage', onStorage);
    if (resizeObserver) resizeObserver.observe(canvas); dialogObserver.observe(document.body, { subtree: true, attributes: true, attributeFilter: ['open', 'hidden', 'inert', 'style', 'class'], childList: true });
    refreshParticles(); renderLearning(); patch(); return controller;
  }
  ns.mount = mount; ns.activate = function (host) { return mount(host).activate(); }; ns.deactivate = function (host) { if (host && host.__capitalCurrentsController) host.__capitalCurrentsController.deactivate(); }; ns.dispose = function () { Array.from(instances).forEach(function (controller) { controller.destroy(); }); };
})(window);
