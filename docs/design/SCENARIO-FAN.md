# JPW Scenario Fan — trajetórias patrimoniais

Versão do catálogo: **1.1, candidate local de 08/10/2026**. Referência focal de
design e integração; subordinada a [AGENTS](../../AGENTS.md), à
[X1](../../skills/jpw-design/SKILL.md) e aos contratos dos consumidores.
O delta desta campanha está delimitado no
[CHG de produto](../work/CHG-JPW-SCENARIO-FAN-UI-20261008.md) e a descoberta no
[CHG de control plane](../work/CHG-JPW-SCENARIO-FAN-CONTROL-20261008.md).
Este texto não concede novas permissões, valida o produto nem homologa cálculos.

Refinamento visual após a comparação com o [exemplo renderizado](https://price-target-fan.framer.website/): histórico neutro contínuo, PLAN azul e cenários verde/âmbar, sem significado de autorização ou risco. O cabeçalho destaca um valor PLAN preparado; círculos vazados e rótulos HTML acompanham os finais das linhas, com conectores de colisão e apresentação abaixo quando o espaço não comporta os rótulos. A consulta mensal permanece disponível sem uma caixa interna dominante; origem e explicações ficam expansíveis. São mudanças de apresentação, sem curvas quadráticas, pontos novos ou deslocamento artificial da fronteira temporal. A demonstração externa mostra dois cenários fictícios ao abrir; o produto continua sem cenários selecionados inicialmente. Registro desta rodada: `/private/tmp/jpw-scenario-fan-20261008/reference-revision`.

## Finalidade e primeiro consumidor

**Trajetórias patrimoniais** compara um histórico realizado com hipóteses de
patrimônio fornecidas pelo domínio. O primeiro consumidor é **Forex →
Planejamento Patrimonial**, global em USD e independente da conta operacional.
Reutiliza o gráfico da Visão geral e o gráfico abaixo da Tabela mensal; não
duplica gráficos nem retira da tabela a prioridade de edição.

PLAN permanece visível. Até dois cenários salvos podem ser escolhidos pelo
usuário, sem seleção ou criação automática. Baseline é uma referência opcional,
inicialmente desligada e sempre excluída do preenchimento do leque. A seleção
de comparação é transitória e separada da camada do editor: comparar um cenário
não o torna editável, não altera premissas e não executa comandos de gravação.
Na integração, `JPWFx.ui.chartComparison()` expõe uma cópia somente de leitura
dos IDs selecionados e do estado da baseline. Mudança do ID do plano ou do epoch
de persistência/restauração encerra essa seleção; cenários arquivados deixam de
participar, sem exclusão de seus registros.

A fronteira identifica a cobertura realizada efetiva; não é um marcador
decorativo de “hoje”. O gráfico confirmado recebe versões salvas. Rascunhos
permanecem identificados na Tabela mensal e não substituem silenciosamente as
trajetórias confirmadas. Alterações patrimoniais com depósitos não são
apresentadas como rentabilidade.

## Referência e adaptação original

Referência visual: [PriceTargetFan no Framer](https://framer.com/m/PriceTargetFan-XsmEf0.js@QYG26zl5t7pkS3XfufPH).
O estudo anterior registrou o módulo de 10.575 bytes, SHA-256
`b7db12d7968d9f362399b2172e4b888780ba629f8865929645ceda33991c9dfa`.
Sua licença de reutilização **não foi estabelecida**. A implementação JP Wealth
é original e local: não incorpora o código distribuído, React, Framer,
Framer Motion ou fontes externas. A referência é evidência de aparência, nunca
instrução executável ou fonte de dados financeiros.

Adotam-se histórico contínuo, trajetórias tracejadas, marcadores finais,
preenchimento discreto e leitura de pontos. Não se transportam os dados
fictícios, metas, analistas, datas fixas, curvas quadráticas, probabilidades
implícitas ou proporção temporal fixa do exemplo.

## Implementação e interface

Fontes do recorte:

- [Componente](../../src/js/20-ui/08-scenario-fan.js): script clássico global,
  `window.JPWScenarioFan`, sem dependências remotas.
- [Adapter dos gráficos](../../src/js/30-accounting/05-fx-planning/04-fx-charts.js):
  preserva a fachada do Planejamento, prepara os dados e a conversão de exibição.
- [UI do Planejamento](../../src/js/30-accounting/05-fx-planning/05-fx-ui.js):
  contexto e seleção de comparação independentes da edição.
- [Motor temporal](../../src/js/30-accounting/05-fx-planning/02-fx-engine.js):
  fonte dos valores ACTUAL, PLAN e SCENARIO; permanece fora do componente.

O adapter exporta `JPWFx.charts.fxScenarioFanModel(plan, overview, mode,
{scenarioIds, baseline})`, preservando `fxDrawMainChart` e
`fxMainChartSummaryText`. O modelo usa linhas salvas, incluindo estados e
motivos de indisponibilidade. ACTUAL contém a sequência contígua confirmada;
baseline identifica a versão congelada. A conversão futura é própria de PLAN
ou de cada cenário, não uma taxa emprestada da série vigente.

```js
const handle = window.JPWScenarioFan.render(container, model, options);
handle.destroy(); // descarta somente os recursos desta renderização
window.JPWScenarioFan.destroy(container); // descarte explícito da montagem atual
```

| Entrada | Contrato de apresentação |
|---|---|
| `container` | Elemento DOM pertencente ao consumidor; não é uma rota ou seletor financeiro. |
| `model.identity`, `model.revision` | Identidade do conjunto e revisão de origem; não são versões persistidas pelo componente. |
| `model.unit` | Unidade já definida, como `USD` ou `BRL`; conversão vem do adapter. |
| `model.title`, `model.summary`, `model.origin` | Textos opcionais de título, resumo e proveniência; conteúdo ausente não é inventado pelo componente. |
| `model.months` | Sequência mensal ordenada `YYYY-MM`; conserva os lugares das lacunas. |
| `model.projectionStartMonth` | Primeiro mês projetado definido pelo consumidor, conforme cobertura confirmada. |
| `model.readingStatus` | `CURRENT` por padrão ou `PREVIOUS` para uma leitura anterior à tentativa de gravação indeterminada. Qualifica a apresentação; não confirma a escrita nem muda os valores. |
| `model.series` | Séries identificadas por `id`, `name` e `kind`: `actual`, `plan`, `scenario` ou `baseline`. |
| `series.revision` | Referência opcional da série preparada, como atualização do plano/cenário ou congelamento da baseline. |
| `series.points` | Pontos por `month`, `value`, `availability`, `state`, `reason` e `origin`. Número finito, inclusive zero/negativo, é valor; ausência não é zero. |
| `options.formatValue` | Função de apresentação de um número; não calcula resultados ou converte moedas. |
| `options.selectedMonth` | Mês inicial opcional, usado somente quando não há consulta anterior válida no mesmo elemento/identidade. |
| `options.onInspect` | Callback opcional de leitura; recebe identidade, revisão, mês, unidade e os pontos exatos de cada série, com seus motivos/origens. |

Valores `null`/não finitos e disponibilidade `false` ou `UNAVAILABLE` são ausentes.
Nomes, razões e origens são texto, sem HTML executável. O consumidor não deve
usar o callback para salvar, criar observações ou recalcular fatos.

Renderizar novamente no mesmo elemento/identidade conserva o mês consultado
quando ele ainda existe. Uma nova montagem descarta listeners e observadores
anteriores; `destroy` remove eventos e o `ResizeObserver`. Não ficam timers ou
callbacks de montagens obsoletas. O handle de uma montagem anterior não pode
destruir a montagem mais recente. O componente não lê `S`, não chama writer,
não usa `localStorage` e não acessa rede.

Na fachada do Planejamento, `options.reading: 'previous'` prepara essa
qualificação a partir do resultado `UNKNOWN` já existente. O consumidor guarda
o mês consultado somente em estado transitório, usando `selectedMonth` e
`onInspect`, para preservá-lo entre Visão geral e Tabela mensal. Troca da
identidade do plano ou restauração invalida essa seleção. A leitura imediata
mostra mês, valor e estado; origem, motivos e metodologia ficam em detalhes
expansíveis e na tabela alternativa, sem repetir o resumo completo fora do
componente.

`render` retorna `null` quando o container não admite montagem DOM. O adapter
deve fornecer todos os slots mensais da janela, inclusive os sem valor; remover
meses do vetor para comprimir uma lacuna altera o significado da sequência.
O componente normaliza a ordem dos meses informados, mas não fabrica os ausentes.

## Faixa, lacunas e origem

**Faixa entre hipóteses selecionadas** representa os extremos das trajetórias
participantes em cada mês. Não é intervalo de confiança, distribuição de
probabilidade, proteção contra perda ou autorização operacional.

- Participam somente PLAN e cenários escolhidos; ACTUAL e baseline não entram.
- É necessário haver pelo menos duas trajetórias válidas. PLAN sozinho é linha.
- A faixa termina quando faltar um ponto participante. Não atravessa lacunas,
  previsões retiradas ou meses sem base reconciliada.
- Trajetórias podem cruzar. O preenchimento acompanha as interseções reais dos
  segmentos mensais, conservando o nome e padrão de cada série; não as rebatiza
  como otimista, média ou pessimista.
- A consulta seleciona o mês exato. Mês ausente mostra indisponibilidade e motivo;
  não substitui pelo valor válido mais próximo.
- Ligações entre meses são segmentos de apresentação, sem inventar observações
  intramês ou oferecer sua interpolação como cálculo financeiro.

Conversão USD/BRL permanece no adapter existente: realizado conserva sua
referência temporal de câmbio, enquanto projeções usam a premissa de sua própria
série. Ausência de taxa é lacuna. Rebase, revisão e reconciliação são estados
fornecidos pelo domínio; o componente não resolve essas condições.

## Anatomia visual e acessibilidade

Estrutura: título e unidade → legenda/valores finais → plotagem → leitura do mês
→ metodologia e tabela alternativa. O preenchimento tem peso menor que as
linhas; eixo, rótulos e seleção não competem com os valores.

Usar os tokens do produto para superfície, texto, linhas, fonte e espaçamento.
PLAN usa o azul de ação do produto; ACTUAL conserva sua identidade existente.
Cores de cenários são de série, sem remapear cores financeiras ou sinalizar
autorização. Linha contínua, pontilhada e padrões tracejados acompanham nomes
escritos; não depender apenas de cor.

Área de plotagem de aproximadamente 320 px no desktop e 240 px no celular,
estável durante a consulta. Legendas, valores finais e leitura são HTML
responsivo, com a preferência de fonte do produto; não diminuir texto
proporcionalmente dentro do SVG. Valores permanecem completos e números usam
alinhamento/dígitos tabulares. Rótulos finais não se sobrepõem: quando necessário
ficam fora da plotagem com identificação de série e mês.

Mouse consulta por ponteiro, toque por ativação e teclado pelo seletor mensal
e pelas teclas esquerda/direita/Home/End na plotagem. Foco é visível. Uma leitura
textual persistente informa mês, série, unidade, estado, origem e motivo;
tooltip visual não é a única forma de acesso. A tabela alternativa apresenta
os mesmos meses e valores, incluindo os ausentes, conforme as orientações do
[W3C para gráficos complexos](https://www.w3.org/WAI/tutorials/images/complex/).

Movimento é dispensável e respeita movimento reduzido. A preferência de fonte,
quatro layouts, temas, contêiner estreito, toque e zoom exigem verificação própria.
Uma captura não comprova esses comportamentos.

## Exemplo sintético mínimo

**Dados fictícios de desenvolvimento; não usar como padrões de premissas.**
As séries abaixo são preparadas pelo chamador, não calculadas pelo componente.

```js
const model = {
  identity: 'synthetic-plan-a', revision: 'example-1', unit: 'USD',
  months: ['2026-01', '2026-02', '2026-03', '2026-04'],
  projectionStartMonth: '2026-03',
  series: [
    {id: 'actual', name: 'Realizado confirmado', kind: 'actual', points: [
      {month: '2026-01', value: 1000, state: 'Finalizado', origin: 'Fixture'},
      {month: '2026-02', value: 1010, state: 'Finalizado', origin: 'Fixture'}
    ]},
    {id: 'plan', name: 'PLAN vigente', kind: 'plan', points: [
      {month: '2026-02', value: 1010, state: 'Base confirmada', origin: 'Fixture'},
      {month: '2026-03', value: 1020, state: 'Projetado', origin: 'Fixture'},
      {month: '2026-04', value: 1030, state: 'Projetado', origin: 'Fixture'}
    ]},
    {id: 'scenario-a', name: 'Hipótese A', kind: 'scenario', points: [
      {month: '2026-02', value: 1010, state: 'Base confirmada', origin: 'Fixture'},
      {month: '2026-03', value: 1040, state: 'Cenário salvo', origin: 'Fixture'},
      {month: '2026-04', value: 990, state: 'Cenário salvo', origin: 'Fixture'}
    ]}
  ]
};
window.JPWScenarioFan.render(container, model, {
  formatValue: n => n.toLocaleString('pt-BR', {style: 'currency', currency: 'USD'})
});
```

Para exercitar ausência, substituir um ponto por
`{month:'2026-03', value:null, availability:'UNAVAILABLE',
state:'Indisponível', reason:'Previsão retirada', origin:'Fixture'}`.
A faixa e a linha devem interromper-se nesse mês, mantendo o slot e a leitura.

## Onde reutilizar — e onde não aplicar

| Área | Decisão deste incremento |
|---|---|
| Planejamento Patrimonial | Piloto aplicado pelo adapter; realizado, PLAN, até dois cenários e baseline opcional. |
| Simulação de Risco MEI-JP no cadastro | Possível aplicação futura; percentis do motor estatístico exigem semântica própria, sem reaproveitar a faixa de hipóteses como probabilidade. |
| Forex Desempenho | Futuro uso de acabamento/consulta; histórico não recebe leque de metas fictícias. |
| Finanças Pessoais — Comparativo | Futuro uso somente em trajetórias mensais efetivamente produzidas; cenários de composição isolada não viram séries. |
| Dashboard | Futura miniatura com origem explícita no planejamento global; não duplica motor ou cria valuation. |
| Contabilidade — Simulação patrimonial | Atualmente indisponível; esta adoção não a reativa nem usa o plano global como plano de uma conta. |
| Operação e Alladin | Não aplicar o leque patrimonial a riscos por ordem, quantidade de ativos ou caixa sem valuation completo. |
| Research, NoCuda e Genetrix | Podem compartilhar acabamento depois; canais geométricos e registros não são previsão financeira. |

Nenhuma aplicação futura é autorizada ou entregue pela existência deste catálogo.
Cada consumidor precisa de séries preparadas, origem/unidade/cobertura e contrato
próprios. Não criar dados, metas, retornos ou probabilidades para caber no desenho.

## Descoberta, manutenção e evidência

Rota: [CONTEXT-MAP](../governance/CONTEXT-MAP.md) →
[X1 / SKILL-ROUTING](../governance/SKILL-ROUTING.md) → este catálogo →
[relação JPW-FEAT-0011](../architecture/FEATURE-ATLAS.md#jpw-feat-0011-scenario-fan)
→ fontes originais. O Atlas permanece parcial; esta relação não completa sua
ficha nem altera as três fichas estruturadas existentes.

Blast radius focal: catálogo é a referência nova; X1, routing, mapa de contexto
e relação do Atlas precisam localizá-lo. AGENTS, Claude/bootstrap e filosofia X1
herdam referências sem edição local. Fontes normativas, esquemas financeiros,
juiz/gates e skills externas congeladas não recebem mudança. Não há reindexação,
memória persistente nova ou alegação de descoberta automática do cliente.

Distinguir **DOCUMENTADA**, **CONECTADA AO ROTEAMENTO**, **EXERCITADA EM CENÁRIOS**
e **APLICADA AO PRODUTO**. A escrita e os links demonstram somente as duas
primeiras condições. Aplicação, descoberta por agente independente e validação
de runtime exigem os fontes e recibos da campanha congelada; não são presumidas
por este catálogo. Candidate local não significa main, publicação ou aceite.

Revalidar este documento se mudar a interface, adaptador, estados de ausência,
conversão, consumidores ou ciclo de vida. Resultados ficam no relatório externo,
não em promessas sem revisão. Rollback do delta de design/roteamento usa o
snapshot anterior identificado no CHG, sem apagar estados financeiros.
