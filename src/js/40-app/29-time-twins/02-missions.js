(function (window) {
  'use strict';
  var ns = window.JPWTimeTwins = window.JPWTimeTwins || {};
  var ids = ['early-start', 'equal-budget', 'contribution-story', 'three-levers', 'next-contribution', 'crossover'];
  var choices = [{ id: 'A', label: 'O investidor A' }, { id: 'B', label: 'O investidor B' }, { id: 'equal', label: 'Os dois têm o mesmo resultado' }];
  var missions = [
    {
      id: 'early-start', title: 'O primeiro passo e o tempo', objective: 'Investigar o que muda quando o mesmo capital começa em meses diferentes.',
      instruction: 'Preveja o saldo maior: A aplica R$ 1.000 no mês zero; B aplica R$ 1.000 no mês 60. Avance até o mês 240, investigue os aportes e repita com taxa zero nos dois cenários.',
      expected: 'Com 6% ao ano, A termina com mais. Com taxa zero, ambos terminam com os mesmos R$ 1.000.',
      explanation: 'A recebe 60 meses adicionais de capitalização. A diferença vem dos rendimentos sobre rendimentos, pois o principal é igual. Com taxa zero, esperar não altera o valor nominal.',
      variable: 'Calendário do aporte; depois, taxa efetiva anual igual nos dois investidores.',
      correctChoice: 'A', reasonChoices: [{id:'time',label:'O mesmo principal de A rende durante mais meses.'},{id:'principal',label:'A termina com mais porque depositou mais dinheiro.'},{id:'always',label:'Começar antes aumenta o saldo mesmo com taxa zero.'}], correctReason: 'time'
    },
    {
      id: 'equal-budget', title: 'Mesmo orçamento, outro calendário', objective: 'Comparar o efeito do calendário mantendo o total nominal aportado em R$ 1.200.',
      instruction: 'A faz doze aportes de R$ 100 nos meses 1 a 12; B faz os mesmos doze nos meses 49 a 60. Preveja, desloque apenas o calendário e observe o resultado no mês 240.',
      expected: 'No cenário inicial A termina com mais, embora ambos depositem R$ 1.200.',
      explanation: 'Cada aporte de A ganha 48 meses adicionais para render. O orçamento é idêntico: o calendário muda o tempo de cada trajetória, não o principal total.',
      variable: 'Calendário dos doze aportes, mantendo valor e quantidade.', correctChoice: 'A',
      reasonChoices: [{id:'calendar',label:'Cada aporte antecipado ganha mais meses para render.'},{id:'budget',label:'A tem um orçamento maior do que B.'},{id:'last',label:'Só o mês do último aporte determina todo o saldo.'}], correctReason: 'calendar'
    },
    {
      id: 'contribution-story', title: 'A história de cada aporte', objective: 'Reconhecer principal, retornos, valor atual e participação de qualquer aporte no saldo.',
      instruction: 'Preveja qual investidor termina com mais. Selecione um aporte no controle “Aporte individual, agrupado por ano”, confira sua participação no mês escolhido e abra a multiplicação período a período. Compare também o saldo sem esse aporte.',
      expected: 'A termina com mais; cada aporte tem principal próprio e cresce somente depois de entrar no cenário.',
      explanation: 'O valor de um aporte é seu principal multiplicado por (1 + taxa mensal) a cada mês após o depósito. A participação divide seu valor atual pelo saldo aplicado naquele mês; ela muda conforme novos aportes entram. Antes do depósito, esse aporte ainda não participa do saldo.',
      variable: 'Aporte selecionado e mês de inspeção; os cenários conservam o mesmo orçamento.', correctChoice: 'A',
      reasonChoices: [{id:'cohort',label:'Cada aporte tem seu próprio tempo de crescimento; a soma das trajetórias forma o saldo.'},{id:'future',label:'Aportes futuros já fazem parte do saldo aplicado.'},{id:'share',label:'A participação percentual de um aporte é fixa para sempre.'}], correctReason: 'cohort'
    },
    {
      id: 'three-levers', title: 'Três alavancas, três efeitos', objective: 'Distinguir os efeitos de prazo, taxa e aporte mensal no saldo, principal e retornos.',
      instruction: 'A e B começam iguais. Prepare uma alteração de prazo, taxa ou aporte mensal por tentativa e registre sua previsão para a alteração escolhida antes de aplicá-la e avançar. Compare saldo final, total depositado e retornos antes de explicar.',
      expected: 'A e B começam iguais. Alterar a taxa conserva o principal; alterar o aporte ou o número de meses com aportes pode mudar também o total depositado.',
      explanation: 'A taxa muda o fator de crescimento. O prazo oferece mais meses e, quando os aportes continuam, mais depósitos. O aporte mensal muda o principal e os rendimentos futuros. Para atribuir uma consequência a uma causa, altere uma variável por tentativa.',
      variable: 'Uma por tentativa: prazo em meses, taxa efetiva anual ou aporte mensal.', correctChoice: 'equal',
      reasonChoices: [{id:'lever',label:'Cada alavanca atua de modo diferente; comparar principal e retornos revela a causa.'},{id:'rate',label:'Aumentar a taxa aumenta automaticamente o dinheiro depositado.'},{id:'same',label:'As três alavancas produzem sempre o mesmo efeito.'}], correctReason: 'lever'
    },
    {
      id: 'next-contribution', title: 'O próximo aporte faz diferença', objective: 'Medir o impacto absoluto e percentual de um aporte adicional contra o cenário original.',
      instruction: 'Os cenários originais são iguais. A recebe R$ 100 extras no mês 1; B recebe R$ 100 extras no mês 120. Preveja o maior impacto e compare cada resultado com seu próprio cenário sem o extra.',
      expected: 'No cenário inicial, o extra de A tem impacto maior no saldo final; ambos acrescentam os mesmos R$ 100 ao principal.',
      explanation: 'O impacto absoluto é a diferença entre o saldo com o extra e o saldo original. O impacto percentual divide essa diferença pelo saldo original. O extra mais cedo tem mais meses para render. Impacto adicional e participação de um aporte usam denominadores diferentes.',
      variable: 'Mês do aporte extra, conservando seu valor e o cenário original.', correctChoice: 'A',
      reasonChoices: [{id:'extra',label:'O mesmo extra começa antes e rende mais; o impacto é medido contra o original.'},{id:'irrelevant',label:'Um extra pequeno não muda o resultado.'},{id:'share',label:'Impacto percentual é sempre igual à participação no saldo final.'}], correctReason: 'extra'
    },
    {
      id: 'crossover', title: 'Quando o rendimento supera o aporte', objective: 'Investigar o primeiro mês em que o rendimento do período supera o aporte daquele período.',
      instruction: 'Preveja se o primeiro cruzamento de um investidor ocorre na primeira metade do prazo, na segunda metade ou não aparece. Avance e encontre o marco. Altere uma premissa e repita: o marco pode mudar de mês ou não existir no horizonte.',
      expected: 'Com os parâmetros iniciais iguais, ambos cruzam no mês 134. Com taxa zero, o cruzamento não aparece.',
      explanation: 'O marco compara o rendimento sobre o saldo de abertura com o aporte feito no fim do mesmo mês. Só contamos meses com aporte positivo. O marco depende das premissas e não significa independência financeira, nem torna os próximos aportes irrelevantes.',
      variable: 'Uma por tentativa: taxa, aporte mensal, capital inicial ou prazo.', correctChoice: 'late',
      reasonChoices: [{id:'period',label:'O rendimento do período pode superar o aporte; o marco depende do saldo e das premissas.'},{id:'freedom',label:'O cruzamento comprova independência financeira.'},{id:'stop',label:'Depois do cruzamento, novos aportes deixam de contribuir.'}], correctReason: 'period'
    }
  ];
  function freeze(value) {
    if (value && typeof value === 'object') { Object.keys(value).forEach(function (key) { freeze(value[key]); }); Object.freeze(value); }
    return value;
  }
  missions.forEach(function (m) {
    m.predictionKind = m.id === 'crossover' ? 'crossover-half' : 'final-balance';
    m.choices = m.id === 'crossover' ? [{ id: 'early', label: 'Na primeira metade do prazo' }, { id: 'late', label: 'Na segunda metade do prazo' }, { id: 'never', label: 'Não há cruzamento aplicável' }] : choices.map(function (c) { return { id: c.id, label: c.label }; });
    freeze(m);
  });
  function get(id) {
    var mission = missions.find(function (m) { return m.id === id; });
    if (!mission) throw new RangeError('A missão solicitada não existe no catálogo.');
    return mission;
  }
  function clone(value) { return JSON.parse(JSON.stringify(value)); }
  function create(id) {
    var descriptor = get(id);
    var s = ns.simulation;
    var a;
    var b;
    if (id === 'early-start') {
      a = s.periodic({ id: 'A', monthlyContribution: 0 });
      b = s.periodic({ id: 'B', initialCapital: 0, monthlyContribution: 1000, startMonth: 60, endMonth: 60 });
    } else if (id === 'equal-budget' || id === 'contribution-story') {
      a = s.periodic({ id: 'A', initialCapital: 0, startMonth: 1, endMonth: 12 });
      b = s.periodic({ id: 'B', initialCapital: 0, startMonth: 49, endMonth: 60 });
    } else {
      a = s.periodic({ id: 'A' });
      b = s.periodic({ id: 'B' });
    }
    var baselineA = clone(a);
    var baselineB = clone(b);
    if (id === 'next-contribution') {
      a.contributions.push({ id: 'A-extra', month: 1, amount: 100 });
      b.contributions.push({ id: 'B-extra', month: 120, amount: 100 });
    }
    return { a: a, b: b, baselineA: baselineA, baselineB: baselineB, mode: id, variable: descriptor.variable };
  }
  ns.catalog = Object.freeze({ ids: Object.freeze(ids), missions: Object.freeze(missions), get: get, create: create });
})(window);
