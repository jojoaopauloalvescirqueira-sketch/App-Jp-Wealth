(function (window) {
  'use strict';
  var ns = window.JPWTimeTwins = window.JPWTimeTwins || {};
  function esc(value) { return String(value).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function button(action, text, extra) { return '<button type="button" data-action="' + action + '" ' + (extra || '') + '>' + text + '</button>'; }
  function options(choices) { return choices.map(function (c) { return '<option value="' + esc(c.id) + '">' + esc(c.label) + '</option>'; }).join(''); }
  function missionButtons() { return ns.catalog.missions.map(function (m, i) { return '<button type="button" data-mission="' + m.id + '"><span>' + (i + 1) + '. ' + esc(m.title) + '</span><small data-status="' + m.id + '">Por explorar</small></button>'; }).join(''); }
  function characterHTML(actor) {
    var hair = actor === 'A' ? 'M27 27 Q28 8 44 12 Q61 8 62 27 L53 22 L46 16 L37 24 Z' : 'M27 27 Q25 11 44 11 Q63 11 62 27 L54 23 L44 25 L34 20 Z';
    return '<figure class="time-twins-character" data-twin-character="' + actor + '"><svg viewBox="0 0 88 110" aria-hidden="true" focusable="false">' +
      '<path class="time-twins-character-shirt" d="M15 102 L18 76 Q22 63 34 61 L54 61 Q66 63 70 76 L73 102 Z"/>' +
      '<path d="M31 65 L44 80 L57 65 M27 81 L25 102 M61 81 L63 102"/>' +
      '<circle cx="44" cy="34" r="20"/><path class="time-twins-character-hair" d="' + hair + '"/>' +
      '<circle class="time-twins-character-eye" cx="37" cy="35" r="1.5"/><circle class="time-twins-character-eye" cx="51" cy="35" r="1.5"/><path d="M38 44 Q44 49 50 44"/>' +
      (actor === 'A' ? '<circle cx="44" cy="90" r="10"/>' : '<rect x="34" y="80" width="20" height="20" rx="2"/>') +
      '<text x="44" y="94" text-anchor="middle">' + actor + '</text></svg><figcaption><strong>Gêmeo ' + actor + '</strong><span>' + (actor === 'A' ? 'A · linha contínua' : 'B · linha tracejada') + '</span></figcaption></figure>';
  }
  function panelHTML() {
    return '<div data-time-twins-root class="time-twins">' +
      '<header class="time-twins-header"><p class="time-twins-eyebrow">Dois investidores fictícios · um experimento por vez</p><h2>Gêmeos do Tempo</h2><p>Dirija o calendário de A e B. Faça uma previsão, observe o dinheiro crescer e investigue de onde veio a diferença.</p></header>' +
      '<div class="time-twins-characters" aria-label="Personagens do experimento">' + characterHTML('A') + characterHTML('B') + '</div>' +
      '<p class="time-twins-assumptions">Modelo educativo: taxa efetiva anual constante, capitalização mensal e aportes no fim do mês. Sem custos, impostos, inflação ou incerteza. Valores fictícios.</p>' +
      '<p data-output="storage" class="time-twins-notice" role="status"></p><div class="time-twins-actions">' + button('reload', 'Recarregar progresso', 'hidden') + '</div>' +
      '<section data-section="home"><h3>O tempo conta uma história</h3><p>A jornada traz seis experimentos curtos. No laboratório, você escolhe as premissas e compara livremente.</p><div class="time-twins-actions">' + button('start', 'Iniciar jornada', 'class="time-twins-primary"') + button('continue', 'Continuar jornada', 'hidden') + button('free', 'Explorar livremente') + '</div></section>' +
      '<nav class="time-twins-missions" aria-label="Missões da jornada">' + missionButtons() + '</nav>' +
      '<div data-section="exercise" hidden></div><footer class="time-twins-footer"><div class="time-twins-actions">' + button('restart', 'Recomeçar jornada') + '</div><div data-section="restart" class="time-twins-notice" hidden role="group" aria-label="Confirmar recomeço"><p>Apagar somente o progresso desta jornada? As outras ferramentas permanecem como estão.</p><div class="time-twins-actions">' + button('confirm-restart', 'Confirmar recomeço') + button('cancel-restart', 'Cancelar') + '</div></div></footer></div>';
  }
  function input(actor, key, label, value, min, max, step, disabled) {
    return '<label>' + esc(label) + '<input data-field="' + actor + '-' + key + '" type="number" inputmode="decimal" value="' + value + '" min="' + min + '" max="' + max + '" step="' + step + '" ' + (disabled ? 'disabled' : '') + '></label>';
  }
  function actorFields(actor, scenario, mode, lever) {
    var id = mode; var t = scenario.horizonMonths; var items = '';
    if (id === 'free' || id === 'three-levers') {
      if (id === 'free') items += input(actor, 'initial', 'Capital inicial (R$)', scenario.initialCapital, 0, 1000000, '.01');
      items += input(actor, 'monthly', 'Aporte mensal (R$)', scenario.contributions.length ? scenario.contributions[0].amount : 0, 0, 100000, '.01', id !== 'free' && lever !== 'aporte');
      items += input(actor, 'rate', 'Taxa efetiva (% a.a.)', scenario.annualRate * 100, 0, 20, '.01', id !== 'free' && lever !== 'taxa');
      items += input(actor, 'horizon', 'Prazo (meses)', t, 1, 360, 1, id !== 'free' && lever !== 'prazo');
      if (id === 'free') {
        items += input(actor, 'start', 'Primeiro aporte (mês)', 1, 1, t, 1);
        items += input(actor, 'end', 'Último aporte (mês)', t, 0, t, 1);
      }
    } else if (id === 'early-start') {
      items += input(actor, 'deposit', 'Mês do único aporte de R$ 1.000', scenario.initialCapital ? 0 : scenario.contributions[0].month, 0, t, 1);
      items += '<p>Um único principal de R$ 1.000; taxa igual para os dois.</p>';
    } else if (id === 'equal-budget') {
      items += input(actor, 'start', 'Início do bloco de 12 aportes', scenario.contributions[0].month, 1, t - 11, 1);
      items += '<p>12 × R$ 100 = R$ 1.200. Só o calendário muda.</p>';
    } else if (id === 'next-contribution') {
      items += input(actor, 'extra', 'Mês do aporte extra de R$ 100', scenario.contributions[scenario.contributions.length - 1].month, 1, t, 1);
      items += '<p>O cenário original mantém seus aportes regulares.</p>';
    } else if (id === 'crossover') {
      items += input(actor, 'rate', 'Taxa efetiva (% a.a.)', scenario.annualRate * 100, 0, 20, '.01');
      items += '<p>Mude apenas a taxa e investigue o marco.</p>';
    } else items += '<p>Agenda fixa: escolha um aporte abaixo para investigar sua trajetória.</p>';
    return '<fieldset><legend>Gêmeo ' + actor + '</legend><div class="time-twins-fields">' + items + '</div></fieldset>';
  }
  function exerciseHTML(state) {
    var free = state.mode === 'free'; var m = free ? null : ns.catalog.get(state.id); var mode = free ? 'free' : state.id;
    var rows = [['balance', 'Saldo aplicado'], ['contributed', 'Total já aportado'], ['pending', 'Aportes futuros (principal)'], ['returns', 'Retornos acumulados'], ['interest', 'Rendimento neste mês'], ['contribution', 'Aporte neste mês'], ['final', 'Saldo no fim do prazo']];
    return '<div class="time-twins-exercise-head"><p class="time-twins-eyebrow">' + (free ? 'Laboratório livre' : 'Jornada guiada') + '</p><h3 tabindex="-1" data-output="title">' + (free ? 'Seu experimento, suas premissas' : esc(m.title)) + '</h3><p>' + (free ? 'Compare premissas fictícias. Altere os campos e avance no tempo; a projeção completa está disponível.' : esc(m.objective)) + '</p><p>' + (free ? 'A e B podem ter prazos diferentes. Depois do prazo, cada saldo permanece no seu valor final.' : esc(m.instruction)) + '</p><div class="time-twins-actions">' + button('journey', 'Voltar à jornada') + button('restore', 'Restaurar exercício') + '</div></div>' +
      '<section aria-label="Preparar experimento"><h4>1. Prepare uma alteração</h4>' + (mode === 'three-levers' ? '<label>Alavanca desta tentativa<select data-field="lever"><option value="prazo">Prazo</option><option value="taxa">Taxa</option><option value="aporte">Aporte mensal</option></select></label>' : '') +
      '<div class="time-twins-pair">' + actorFields('A', state.draft.a, mode, state.lever) + actorFields('B', state.draft.b, mode, state.lever) + '</div>' +
      (mode === 'early-start' ? '<div class="time-twins-actions">' + button('zero', 'Repetir com taxa zero') + button('positive', 'Repetir com taxa de 6%') + '</div>' : '') + '<p data-output="validation" role="alert"></p><p data-output="lever-note"></p></section>' +
      '<section data-section="prediction" ' + (free ? 'hidden' : '') + '><h4>2. Antes de avançar, faça sua previsão</h4><label>' + (mode === 'crossover' ? 'Quando ocorre o primeiro cruzamento do investidor selecionado abaixo?' : 'Quem terá o maior saldo ao fim do prazo preparado?') + '<select data-field="prediction"><option value="">Escolha uma previsão</option>' + (m ? options(m.choices) : '') + '</select></label><div class="time-twins-actions">' + button('predict', 'Confirmar previsão e aplicar', 'class="time-twins-primary"') + '</div><p data-output="forecast" role="status"></p></section>' +
      '<section aria-label="Linha do tempo"><h4>' + (free ? '2' : '3') + '. Avance e observe</h4><p data-output="timeline-label"></p><label>Mês observado<input data-field="month" type="range" min="0" max="240" value="0" step="1"></label><div class="time-twins-actions">' + button('step-prev', '−1 mês') + button('step-next', '+1 mês') + button('step-year', '+12 meses') + button('play', 'Executar') + '</div><p data-output="feedback" role="status" aria-live="polite"></p>' +
      '<div class="time-twins-chart"><svg viewBox="0 0 600 260" role="img" aria-label="Saldo de A e B por mês; mesma escala vertical. Valores na tabela abaixo."><text x="48" y="15" data-output="chart-max"></text><line x1="48" y1="26" x2="48" y2="225"/><line x1="48" y1="225" x2="580" y2="225"/><text x="4" y="229">R$ 0</text><text x="48" y="249">mês 0</text><text x="500" y="249" data-output="chart-end"></text><path class="time-twins-line-a" data-chart-line="A"/><path class="time-twins-line-b" data-chart-line="B"/><path class="time-twins-line-cohort" data-chart-line="cohort"/><path class="time-twins-line-without" data-chart-line="without"/><text data-chart-marker="A"></text><text data-chart-marker="B"></text></svg><p class="time-twins-legend"><span class="time-twins-key-a">━ A</span> <span class="time-twins-key-b">┄ B</span> <span>· Aporte selecionado</span> <span>┄ Sem este aporte</span></p></div>' +
      '<div class="time-twins-table-wrap"><table data-output="totals"><caption>Valores no mês observado</caption><thead><tr><th scope="col">Medida</th><th scope="col">A <small data-output="status-A"></small></th><th scope="col">B <small data-output="status-B"></small></th></tr></thead><tbody>' + rows.map(function (row) { return '<tr><th scope="row">' + row[1] + '</th><td data-output="' + row[0] + '-A"></td><td data-output="' + row[0] + '-B"></td></tr>'; }).join('') + '</tbody></table></div><p data-output="extra-A"></p><p data-output="extra-B"></p><p data-output="crossover-A"></p><p data-output="crossover-B"></p>' + (mode === 'crossover' || free ? '<div class="time-twins-actions">' + button('cross', 'Investigar cruzamento') + '</div>' : '') + '</section>' +
      '<section aria-label="Inspecionar um aporte"><h4>' + (free ? '3' : '4') + '. Investigue uma trajetória</h4><div class="time-twins-fields"><label>Gêmeo para inspeção<select data-field="actor"><option value="A">Gêmeo A</option><option value="B">Gêmeo B</option></select></label><label>Aporte individual, agrupado por ano<select data-field="cohort"></select></label></div><p data-output="inspection"></p><div class="time-twins-actions">' + button('trace', 'Abrir fórmula mês a mês', 'aria-expanded="false"') + button('without', 'Comparar sem este aporte', 'aria-pressed="false"') + '</div><div class="time-twins-trace" data-section="trace" hidden><p>Valor = principal × (1 + taxa mensal) elevado aos meses decorridos. Não há arredondamento intermediário.</p><table data-output="trace"><caption>Capitalização mensal do aporte selecionado</caption><thead><tr><th>Mês</th><th>Multiplicador</th><th>Valor</th></tr></thead><tbody></tbody></table></div></section>' +
      '<section data-section="reason" ' + (free ? 'hidden' : '') + '><h4>5. Explique o que mudou</h4><label>Qual relação explica este experimento?<select data-field="reason"><option value="">Escolha uma explicação</option>' + (m ? options(m.reasonChoices) : '') + '</select></label><div class="time-twins-actions">' + button('reason', 'Verificar explicação') + button('help', 'Ver explicação') + '</div><p data-output="reason-feedback" role="status"></p><p data-output="explanation" hidden></p><p data-output="requirements"></p><div class="time-twins-actions">' + button('complete', 'Concluir missão', 'class="time-twins-primary" disabled') + button('assisted', 'Avançar com explicação', 'hidden') + button('skip', 'Pular missão') + button('repeat', 'Repetir') + button('previous', 'Anterior') + button('next', 'Próxima') + '</div></section>';
  }
  ns.view = Object.freeze({ panelHTML: panelHTML, exerciseHTML: exerciseHTML, escape: esc });
})(window);
