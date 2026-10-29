# Caixa Anual — revisão da primeira aba Todas

Candidato local conferido: build `fc1a41530cdc4569`, branch `codex/caixa-anual-revisao-20261028`, HEAD `3e24f60f8cfe87f79335f40e95a0927379a9f834`. Referência: primeira aba **Todas!A2:R329** de Planejamento_com_aporte copy.xlsx, SHA256 `621a4e5bdefc467bede301b94e2c6f60aa05c78df3613cfac3908ef8d0c9084a`. As demais abas não integram esta revisão. Não houve importação de valores pessoais nem alteração do original.

[Abrir prévia versionada](http://127.0.0.1:61534/index.html?v=fc1a41530cdc4569). A origem local é nova, para evitar uma versão anterior em cache; os dados dos outros endereços não foram transferidos nem apagados. [Identidade HTTP e arquivos](fresh-preview-identity.json).

## Conclusão

O núcleo de planejamento anual e fechamento diário preserva a função da primeira aba e as adaptações aprovadas. Não foi demonstrado erro de fórmula nos 14 casos sintéticos independentes. A apresentação ainda tem duas incoerências confirmadas e uma limitação de data aproximada que precisam ficar claras antes de afirmar excelência do conjunto. A renomeação para **Caixa Anual** foi autorizada e implementada sem alterar essas regras ou corrigir silenciosamente os achados.

O FULL atual terminou com **116/116 PASS e saída real 0**, em 28/10/2026, das **11h58min13s às 12h48min37s**, horário de São Paulo. Esse resultado técnico não resolve os achados independentes nem substitui o aceite humano.

## O que foi preservado

| Função da aba Todas | Resultado observado |
|---|---|
| Planejado e Realizado lado a lado | Blocos e tabela separados no computador; 3 colunas com detalhes no compacto. |
| Meta anual, diária e mensal | Composição e bases originais mantidas; meta e tempo proporcionais usam a mesma fração, sem segundo redutor. |
| Programação | Dias/semana×52×meses/12 preservado, distinto das datas civis do calendário. |
| Registro diário e saldo encadeado | Resultado monetário manual com prévia e confirmação; correção/anulação auditadas no escritor canônico. |
| Semanas e acompanhamento | Subtotais civis; dias decorridos, fechamentos e declarações distintos; vazio não vira zero. |
| Termômetro | Busca aproximada da abertura projetada, direção em texto e cores nos limites 13/14/29/30 preservadas. |
| Fechamento anual do site | Ato explícito após 31/12, pendências resolvidas e retrato versionado; não encerra operações Forex. |

O site usa calendário civil coerente e exclui somente datas declaradas, conserva saldos observados, bloqueia taxas dependentes de sequências incompletas e separa projeção de confirmação. Essas são adaptações aprovadas, não reprodução literal de inconsistências das sementes de data do Excel. O módulo não é um razão completo de entradas/saídas: não soma automaticamente operações, aportes ou saques; os resultados diários continuam manuais, como no contrato.

## Achados materiais

1. **UX-01 — PRODUCT_FAIL de apresentação, P2:** após correção válida de um fechamento anterior, o retorno pode usar abertura real de 1.200 enquanto o cabeçalho mostra abertura planejada de 1.000 sob o nome genérico Saldo inicial. Cálculo correto de 1.212/1.200−1 = 1%; denominador não exposto no resumo. Preservar ambas e identificar planejada versus real, sem sobrescrever a programação. [Prova](review/opening-divergence.png).
2. **UX-02 — PRODUCT_FAIL de apresentação, P2:** sem datas pendentes mas com divergência de saldo, a nota diz Registros conferidos. O alerta de reconciliação e os bloqueios de taxas/fechamento permanecem; o texto afirmativo é contraditório. Recomenda-se derivar o texto do estado completo. [Resumo](review/conflicting-status.png) · [Alerta preservado](review/reconciliation-warning.png).
3. **Limitação matemática aprovada / orientação:** a programação Q pode diferir do número de datas da grade. Em exemplo sintético com saldo de 1.000, meta de 25%, ano 2026 e 6 dias por semana, Q = 312 e 261 datas produzem saldo projetado final de 1.205,23 para objetivo de 1.250,00. A busca aproximada ainda retorna 31/12. Não é prova de meta atingida. Expor saldo projetado de 31/12 e qualificar a data sem alterar a fórmula preservada por inferência.

As duas falhas foram observadas em contexto isolado com writer e consultas reais; não foram inferidas somente de leitura de código. A correção desses achados **não integra a autorização de renomeação**. Revisões [matemática](review/MATH-REVIEW.md) e [de jornadas](review/UX-REVIEW.md), [resultados 14/14](review/math-results.json) e [receitas/estados sintéticos](review/ux-concerns.json). Nenhum dado real foi usado nas reproduções.

## Nome e verificação

Caixa Anual substitui o nome público em navegação, título, nome acessível, Dashboard, Notas, Dante, ajuda e atalho Forex. IDs management-accounting/management/contab, aliases e progresso permanecem. [Desktop renomeado](caixa-anual-desktop.png) · [Estado vazio](caixa-anual-empty.png). As capturas dos achados preservam o nome anterior para provar o estado revisado.

Três verificadores alterados apenas nas expectativas literais autorizadas: Notas com 12 casos GREEN, navegação com 4 layouts GREEN, jornada anual GREEN. Os mesmos juízes falharam no nome antigo (RED); contraprovas separadas dos aliases management/contab rejeitaram o rótulo antigo sem mudar bytes do disco. [Revisão independente dos rótulos](controls/independent-label-review.json).

A quarta expectativa da trilha foi autorizada especificamente em call_ca4bee2bb5904219b50f6cd1762a1791 e aplicada em uma constante. O mesmo juiz rejeitou o nome antigo numa resposta HTML mutada somente em memória. O caso completo é **suplementar e já estava fora dos 116 checks do FULL**; depois do rótulo corrigido, ele encontra uma expectativa herdada na rota research-stocks-br. O juiz original do baseline e o nome antigo em memória reproduziram a mesma falha posterior. Essa comparação é controlada, não um checkout integral da base. O focal suplementar completo permanece **BASELINE_FAIL**, sem alterar seus outros critérios. As primeiras duas tentativas de injeção JS foram **TEST_HARNESS_FAIL** de contraprova, pois não alteraram o breadcrumb efetivo lido do DOM. Nenhuma dessas tentativas é apresentada como RED do produto. O catálogo obrigatório não mudou nem perdeu esse caso por esta entrega. [Classificação independente final](controls/sidebar-classification-final.json).

## Validação do candidato final

- [Recibo FULL](full-final.json): 116 PASS, zero resultados nas demais classificações; SHA256 `013522eba409dbaa97e64303725ffe46dfdb03f8b1bb51e84a91f51a71cc893c`. [Saída real do processo](full-exit.json) e [log](full-output.log).
- Matriz visual: 413/413 casos PASS, critérios e tolerância de 2 px preservados, 870,061 segundos dentro do limite original de 900 segundos. A cobertura de Gerenciamento também passou em quatro layouts, dois temas, 320–1.440 px e fronteira dos 900 px úteis. Os checks de zoom nativo do catálogo passaram.
- Distribuições: reconstrução oficial, HTTP, PWA offline, arquivo local, portátil, backup e recuperação passaram nos verificadores atuais. O processo não criou dependências nem alterou recursos financeiros.
- Preservação: os 1.624 arquivos de entrada congelados não mudaram durante a rodada. Os 3.454 arquivos da referência continuam presentes; as 25 diferenças estão inventariadas. O catálogo conserva os mesmos 116 checks e a mesma ordem, e o arquivo quality_gate.py não mudou. [Auditoria final](FINAL-AUDIT.json).
- Um teste unitário existente regravou somente o timestamp de um recibo histórico. A saída nova foi preservada separadamente e os bytes anteriores do recibo foram restaurados a partir do arquivo de referência após a suíte. [Registro da restauração](controls/historical-receipt-restored.json). Isso não alterou produto, juízes ou resultado do gate.

[Revisão independente final](INDEPENDENT-FINAL-REVIEW.md). O FULL aprovado cobre seus casos declarados; os dois defeitos de apresentação, a falha suplementar e as causas históricas de Epoch/Alladin permanecem separadamente abertos. Não há declaração de prontidão integral.

## Cobertura e limites

Revisão atual: OOXML/fórmulas/estilos, 14 casos puros executados, jornadas reais de plano/cancelamento/resultado/correção/anulação/ano elegível/histórico, desktop de 1.440 px e celular de 390 px sem overflow, 19 capturas e seleção Forex preservada. [Observações](review/ux-observations.json).

NÃO VERIFICADO nesta revisão: execução e recálculo no Excel nativo, igualdade visual integral da aba, toque físico, leitor de tela, Safari e aceite humano. Renderização parcial por artifact_tool foi usada apenas para composição, sem validar seus valores recalculados e sem copiar a imagem com valores pessoais para o repositório. Automação e capturas não constituem teste humano.

## Preservação e próximos passos

Referência de 3.454 arquivos e 300 arquivos pendentes preservada antes da branch. Motores anual/estado, writer canônico, política, persistência e dados permanecem sem alteração. Não houve commit, merge, push ou publicação. [Avaliação delimitada de impacto agêntico](AGENTIC-IMPACT.md), sem alteração de instruções, plugins ou memória global. A proteção temporária contra suspensão terminou com a suíte; o Mac está liberado para uso normal.

Recomendação mínima posterior: resolver a clareza das duas aberturas, a indicação de reconciliação e a explicação de objetivo/data aproximada; conservar cálculos e dados. Compactação do resumo no celular é hipótese de melhoria de eficiência, não defeito confirmado: o fluxo continua alcançável por rolagem.
