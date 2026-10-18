/* Educational presets only. Every trajectory uses the shared field engine. */
(function (global) {
  'use strict';
  var ns = global.JPWCapitalCurrents = global.JPWCapitalCurrents || {};
  function freeze(value) {
    Object.keys(value).forEach(function (key) { if (value[key] && typeof value[key] === 'object') freeze(value[key]); });
    return Object.freeze(value);
  }
  var items = [
    { id: 'intro-field', kind: 'intro', title: 'Uma seta em cada ponto',
      explanation: 'O eixo horizontal é a pressão efetiva q, de −1 a 1. O vertical é o deslocamento do preço p, de −6 a 6 pontos fictícios, em relação a uma referência inicial. Nenhum eixo é tempo. Cada ponto representa um estado possível.',
      goal: 'Reconheça a direção indicada pelo campo em um ponto.', instruction: 'Selecione um ponto e avance para acompanhar sua trajetória.',
      expected: 'A trajetória acompanha as setas locais; o tempo aparece no contador separado.' },
    { id: 'intro-pressure', kind: 'intro', title: 'Aplique e retire pressão',
      explanation: 'A pressão aplicada u é um comando. A pressão efetiva q responde aos poucos e determina a direção do preço.',
      goal: 'Distinga o comando aplicado da pressão que ainda atua.', instruction: 'Aplique pressão, avance até observar q diferente de zero, retire a pressão e avance novamente.',
      expected: 'Ao retirar u, q decai gradualmente. O preço mantém sua direção enquanto q não for zero.' },
    { id: 'intro-depth', kind: 'intro', title: 'A mesma pressão, outra profundidade',
      explanation: 'No mesmo ponto, uma profundidade menor aumenta a velocidade do preço quando q é diferente de zero.',
      goal: 'Compare as setas no mesmo estado com profundidades diferentes.', instruction: 'Escolha um ponto com q diferente de zero. Altere somente a profundidade e compare a seta antes de avançar.',
      expected: 'A componente vertical muda. Com q e u iguais a zero, mudar a profundidade mantém o preço constante.' },
    { id: 'release-pressure', kind: 'discovery', title: 'Depois de retirar a pressão',
      explanation: 'Duas trajetórias partem de q = 0,6 e p = 0. Uma retira a pressão aplicada; a outra mantém u = 0,6.',
      goal: 'Observe a pressão residual depois de retirar o comando.', instruction: 'Compare as duas trajetórias durante 1 segundo, com o mesmo estado inicial e as mesmas escalas.',
      expected: 'Sem comando, q diminui e o preço ainda avança; com pressão mantida, q permanece em 0,6.' },
    { id: 'same-pulse-depth', kind: 'discovery', title: 'O mesmo pulso, duas profundidades',
      explanation: 'O mesmo pulso atua sobre dois campos uniformes. Só a profundidade muda: 1 e 0,5.',
      goal: 'Compare o efeito da profundidade sob o mesmo comando.', instruction: 'Observe u = 0,8 por 1,5 segundo e depois u = 0 por 3 segundos, partindo de q = 0 e p = 0.',
      expected: 'Durante estes 4,5 segundos, as pressões efetivas coincidem e a menor profundidade produz maior deslocamento de preço.' },
    { id: 'shallow-band', kind: 'discovery', title: 'Atravessar uma faixa rasa',
      explanation: 'Uma faixa de menor profundidade altera localmente a velocidade do preço. Ela não acrescenta força ao modelo.',
      goal: 'Observe a velocidade ao atravessar a região menos profunda.', instruction: 'Compare por 5 segundos o perfil uniforme e a faixa rasa, ambos começando em q = 0,4 e p = −1, com u = 0,4.',
      expected: 'A pressão efetiva permanece igual nos dois percursos; a trajetória acelera verticalmente na faixa, cuja profundidade mínima é 0,4.' }
  ];
  function get(id) { return items.find(function (item) { return item.id === id; }) || null; }
  function copy(state) { return { q: state.q, p: state.p, t: state.t }; }
  function experiment(id) {
    var item = get(id);
    if (!item || item.kind !== 'discovery') throw new RangeError('Descoberta desconhecida.');
    var initial = { q: 0.6, p: 0, t: 0 }, ticks = 60;
    var paramsA = { u: 0, tau: 1, kappa: 2, depth: 1, profile: 'uniform' };
    var paramsB = { u: 0.6, tau: 1, kappa: 2, depth: 1, profile: 'uniform' };
    var labelA = 'Pressão retirada: u = 0 por 1 segundo', labelB = 'Pressão mantida: u = 0,6 por 1 segundo';
    if (id === 'same-pulse-depth') {
      initial = { q: 0, p: 0, t: 0 }; ticks = 270;
      paramsA.u = paramsB.u = 0.8; paramsB.depth = 0.5;
      labelA = 'Profundidade 1: u = 0,8 por 1,5 s; depois u = 0 por 3 s';
      labelB = 'Profundidade 0,5: u = 0,8 por 1,5 s; depois u = 0 por 3 s';
    } else if (id === 'shallow-band') {
      initial = { q: 0.4, p: -1, t: 0 }; ticks = 300;
      paramsA.u = paramsB.u = 0.4; paramsB.profile = 'band';
      labelA = 'Perfil uniforme: u = 0,4 por 5 segundos'; labelB = 'Faixa rasa: u = 0,4 por 5 segundos';
    }
    function series(params) {
      var result = [copy(initial)], active = Object.assign({}, params);
      for (var i = 0; i < ticks; i++) {
        if (id === 'same-pulse-depth' && i === 90) active.u = 0;
        result.push(ns.engine.advance(result[result.length - 1], active, ns.engine.DT));
      }
      return result;
    }
    return { id: id, initial: copy(initial), duration: ticks * ns.engine.DT, labelA: labelA, labelB: labelB,
      a: series(paramsA), b: series(paramsB), paramsA: paramsA, paramsB: paramsB };
  }
  freeze(items);
  ns.catalog = Object.freeze({ items: items, get: get, experiment: experiment });
})(window);
