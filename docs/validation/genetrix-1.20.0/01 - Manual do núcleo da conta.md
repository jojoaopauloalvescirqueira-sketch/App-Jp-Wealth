# GENETRIX 1.20.0 — Manual do núcleo da conta

Guia do candidato · 6 de outubro de 2026 · Português

Este manual explica a organização proposta na revisão 1.20.0. Consulte os recibos da entrega para saber quais testes foram realmente executados. As ilustrações são esquemas didáticos; não são capturas do MT5 nem comprovam instalação ou funcionamento nativo. Sem evidência específica, interação e aceite operacional permanecem `NOT_RUN`.

## 1. O que colocar em cada gráfico

O **GENETRIX · Núcleo da conta**, arquivo `JPW_Genetrix_Monitor.mq5`, reúne monitoramento e contabilidade em um EA observacional. Ele acompanha a conta conectada nessa instalação do terminal, inclusive posições e pendentes de outros instrumentos. O símbolo do gráfico de apoio não limita esse acompanhamento.

No seu gráfico de trabalho, mantenha os indicadores **Genetrix · Conta**, arquivo `JPW_Alavancagem_Atual.mq5`, e **NoCuda · Gráficos**, arquivo `JPW_NoCuda_Channels.mq5`. O primeiro exibe resumo e Cockpit; o segundo conserva os estudos técnicos e desenhos. Abrir os painéis não inicia o núcleo.

![Organização dos gráficos](assets/manual-account-map.png)

O MT5 permite um EA por gráfico. Anexar um segundo EA ao mesmo gráfico retira o anterior. Por isso, use um **gráfico de apoio dedicado** para o núcleo. Se você já opera outro EA no gráfico de trabalho, ele pode permanecer ali com os dois indicadores. O Supervisor 7x, quando usado e validado, ocupa outro gráfico próprio.

O **Supervisor 7x é opcional e separado**. Não é necessário para observar a conta, contabilizar ciclos ou mostrar as sete métricas. Esta instalação padrão não o anexa nem o arma. Sua disponibilidade e eventual execução demo exigem avaliação e autorização próprias.

## 2. Quais componentes alimentam as informações

| Informação | Origem | O que pode impedir um valor atual |
| --- | --- | --- |
| Alavancagem utilizada | Indicador: posições, especificações, conversões e equity | Dados inconsistentes, unidade ou conversão não confirmada, equity inválida |
| Flutuante | Indicador: resultado flutuante e saldo | Saldo inválido, contexto ou conexão não confirmado |
| Genesis SL | Indicador: referência vinculada, cotação e SL | Referência ambígua, encerrada ou sem SL; cotação indisponível |
| Raiz N de uma semana | Indicador: preço, ATR55 H4, calendário e F diagnóstico | Insumos, tempo ou configuração não confirmados |
| Raiz N de duas semanas | Indicador: mesmos insumos, horizonte distinto | Mesmas limitações, avaliadas por horizonte |
| Risco dos stops | Módulo de monitoramento do núcleo | Captura antiga, SL ausente, agrupamento ou composição não confirmado |
| Flutuante compensado | Módulo de contabilidade do núcleo | Ciclo não selecionado, cobertura incompleta, custos sem evidência, captura antiga |

O monitoramento também produz **Histórico Pessoal**, episódios de ausência de SL, avisos e máximos observados de alavancagem. A contabilidade mantém o ledger dos ciclos inferidos. Os bancos existentes continuam separados; essa revisão não transforma todos os registros em um único banco nem altera as fórmulas financeiras.

Ter o núcleo funcionando não garante que todas as sete linhas tenham um número. Quando falta evidência, a resposta correta é mostrar a limitação e seu motivo. Os ciclos contábeis inferidos não certificam a Operação formal V11. Resultado compensado não restaura Risco Comprometido ou orçamento.

## 3. Como entender a aba Sistema

Abra **Genetrix · Conta → Sistema**. O quadro **Componentes da conta** apresenta função, versão/build declarados, gráfico de origem, identificação abreviada do produtor e estado de cada módulo.

![Presença, captura e cobertura](assets/manual-state-map.png)

Leia três informações separadamente:

1. **Presença:** existe um sinal recente do produtor? Um heartbeat recente indica presença declarada; não prova execução contínua nem valida a métrica financeira.
2. **Última captura:** quando esse módulo aceitou dados? Atualizar o heartbeat não renova a captura. Uma captura antiga continua antiga.
3. **Cobertura e qualidade:** os dados e custos necessários estão demonstrados? Um módulo pode estar presente e sua contabilidade ser `Partial`.

| Estado apresentado | Significado | Próximo passo |
| --- | --- | --- |
| Ausente ou indisponível | Diagnóstico compatível não foi confirmado | Conferir núcleo no gráfico de apoio, mesma instalação e aba Experts; o motivo distingue ausência de falha de leitura |
| Preparando | Coleta ou reconciliação em andamento | Aguardar progresso; se permanecer parado, consultar motivo e registros |
| Cobertura incompleta | Origem histórica ou custos não foram demonstrados | Reunir evidência do período e dos custos; não marcar confirmação apenas para obter um número |
| Conflito de produtor | Outro produtor ou lock impede o módulo | Conferir instâncias antigas; não apagar locks ou bancos para forçar funcionamento |
| Antigo / Historical | Última captura não confirma a situação atual | Verificar núcleo, conexão e recuperação; preservar o registro histórico |
| Falha | Leitura, coleta ou gravação foi recusada | Usar motivo e aba Experts; o outro módulo pode continuar quando saudável |
| Current | Captura aceita segundo o contrato daquele módulo | Conferir também a qualidade da métrica e o escopo; não equivale a homologação |

O progresso percentual representa **preparação daquela tentativa**, não porcentagem de cobertura histórica, confiança ou conclusão de uma auditoria. Os registros do Supervisor são apresentados como registros; um arquivo antigo não comprova atividade ou armamento atual.

## 4. Instalação com preservação

![Sequência de instalação](assets/manual-install-flow.png)

1. **Identifique o terminal correto.** Abra Arquivo → Abrir pasta de dados. Confira a conta e a instalação sem trocar a conta operacional. Não use somente a pasta de instalação do programa como destino dos fontes.
2. **Guarde o estado anterior.** Preserve o pacote completo, fontes, EX5, dependências, modelos/perfil dos gráficos e preferências. Registre quais EAs e indicadores estão anexados. Preserve os bancos de Diagnostics, MDD, Stop Risk, Raiz N, Gênese, ledger e Histórico Pessoal. Não os substitua pelo conteúdo do pacote.
3. **Use um conjunto coerente 1.20.0.** Confira manifesto e hashes. Copie apenas os componentes previstos para uma validação isolada; não sobreponha toda a pasta MQL5. Não combine um indicador novo com includes antigos ou renomeie um EX5 anterior como nova versão.
4. **Compile os fontes exatos.** No MetaEditor, confira dependências, logs completos e arquivos EX5 recém-gerados. Registre build do compilador e hashes. O código de retorno isolado do processo não substitui o log. Compilação não comprova interação ou recuperação no MT5.
5. **Prepare o gráfico de apoio.** Antes de iniciar o núcleo, retire de seus gráficos os produtores legados `JPW_Alavancagem_Observer` e `JPW_Genetrix_Accountant`. Não os mantenha ativos junto ao novo núcleo. Não apague registros ou locks; deixe o encerramento normal liberar a titularidade.
6. **Anexe somente `JPW_Genetrix_Monitor`.** Use o gráfico de apoio dedicado. Negociação automática não é necessária para esse EA observacional. Mantenha os defaults de cobertura histórica e custos em `false` enquanto faltarem as evidências solicitadas.
7. **Abra os consumidores.** No gráfico de trabalho, anexe os dois indicadores previstos, preservando os estudos existentes e suas preferências. Abra Genetrix · Conta → Sistema e confira presença, captura, módulos e motivos.
8. **Faça a conferência nativa.** Confirme resumo, dois acessos, alternância de abas, desenhos, rascunhos, registros e recuperação após reinício em ambiente isolado. Os percursos críticos exigem três sessões novas. Registre todas as tentativas antes de considerar a aplicação operacional.

Se houver conflito, não inicie produtores adicionais para tentar resolver. Verifique primeiro se uma instância legada ou outro Monitor já acompanha a mesma conta e instalação. Consultar registros não troca a conta conectada do terminal.

## 5. Uso diário e flutuante compensado

Mantenha o gráfico de apoio aberto enquanto desejar acompanhamento. **Fechar o Cockpit mantém o resumo e não encerra o EA. Fechar o gráfico de apoio, remover o EA ou substituí-lo encerra aquele acompanhamento.** O comportamento com o gráfico minimizado precisa estar confirmado nos recibos nativos desta revisão; não trate a ilustração como esse teste.

O núcleo pede timer de um segundo, mas o terminal pode atrasar seu despacho. Se um evento de timer já estiver enfileirado ou em processamento, outro não é adicionado à fila. Preparação, gravação e chamadas nativas podem consumir tempo. O diagnóstico mostra progresso, adiamentos e problemas; o histórico não demonstra que todos os picos entre capturas tenham sido observados.

Para o **flutuante compensado**, confira a leitura do ledger e selecione o ciclo quando houver mais de um. Ele reúne o resultado atribuído aos deals e o flutuante remanescente daquele ciclo, incluindo custos atribuíveis conforme o núcleo existente. O percentual usa o saldo da amostra. Não some ciclos diferentes sob o nome de uma única Operação formal.

Os inputs `InpHistoryCoverageConfirmed`, `InpCostCoverageConfirmed` e `InpCoverageEvidence` pertencem ao núcleo. Confirmação exige evidência da conta, origem/zeragem, período e custos. Consultar o histórico do MT5 com sucesso não demonstra, sozinho, que a corretora forneceu toda a história. Os defaults `false` são preservados. Em conta fora do modo suportado pelo ledger v1, a indisponibilidade permanece explícita.

No **Histórico Pessoal**, consulte ocorrências sem SL, máximos observados, detalhes e cobertura. Um aviso informa “sem SL registrado na corretora”; não certifica infração estatutária e não conhece stops virtuais de terceiros. Fechar uma janela de aviso não resolve o episódio.

No **NoCuda · Gráficos**, continue usando os estudos e ações de confirmação próprios. Abrir a aba Sistema, redimensionar ou alternar painéis não deve aplicar um rascunho técnico, alterar fórmula financeira ou armar o Supervisor.

## 6. Solução de problemas

| O que você vê | Confira primeiro |
| --- | --- |
| Apenas o botão NoCuda | Ctrl+I deve listar também `JPW_Alavancagem_Atual`; confirme compilação e anexação do indicador principal |
| Resumo presente, núcleo ausente | EA `JPW_Genetrix_Monitor` no gráfico de apoio, inicialização na aba Experts e mesma instalação |
| Núcleo presente, stops N/A | Motivo da métrica, última captura, composição, SL e escopo; presença não valida o total |
| Núcleo presente, compensado Partial | Evidências de histórico e custos; não mude os defaults para ocultar a falta |
| Compensado sem ciclo selecionado | Escolha explicitamente o ciclo correspondente; vários ciclos não viram uma Operação única |
| Conflito de produtor | Lista de EAs do terminal, núcleos duplicados e produtores legados; encerrar a instância correta normalmente |
| Heartbeat recente, captura antiga | Progresso e motivo do módulo; heartbeat não atualiza a idade dos dados financeiros |
| Supervisor ausente | Situação esperada na instalação observacional padrão; não instale ou arme para liberar outra métrica |
| Falha de gravação | Motivo e armazenamento; preservar banco e evidências, sem recriação silenciosa |
| Valores somem após desconexão | Reconexão e revalidação; indisponibilidade não deve virar zero |

## 7. Rollback sem perder o histórico

![Sequência de rollback](assets/manual-rollback-flow.png)

1. Registre o incidente, versão/build e mensagens antes de alterar a instalação. Preserve os arquivos atuais e as evidências da tentativa.
2. Remova o novo Monitor normalmente do gráfico de apoio. Confira a liberação de seus produtores antes de iniciar componentes anteriores. Não apague locks ou bancos.
3. Restaure o conjunto anterior coerente de indicadores, EAs e includes a partir do backup daquela instalação. Se voltar à arquitetura anterior, Observer e Accountant usam gráficos próprios, um EA por gráfico. Supervisor permanece opcional e não é armado pelo rollback.
4. Restaure modelos e preferências somente do backup correspondente, quando necessário. Não sobrescreva os registros financeiros novos para recuperar apenas a interface.
5. Reabra a aba Experts e confira presença, qualidade das leituras e ausência de duplicação. Se o histórico ou alguma leitura não puder ser confirmado, mantenha essa limitação registrada.

## 8. O que esta revisão comprova e como conferir

Use manifesto, hashes, logs e relatórios da revisão exata. A entrega mantém separados **candidato de fontes**, **compilação nativa**, **teste local**, **interação no terminal**, **instalação** e **aceite operacional**. Uma etapa favorável não aprova automaticamente as demais. Fontes e testes de 1.19.0 não são evidência de execução de 1.20.0.

Os 24 casos `CORE-AC01…24` foram congelados antes da implementação. Cada caso exige três processos novos, e os percursos nativos críticos exigem três sessões novas. As contagens realizadas, falhas preservadas e pendências estão nos relatórios da entrega; este manual não atribui aprovação aos casos.

Estados como `Current`, `Estimated`, `Partial`, `Historical`, `N/A`, `PENDING`, `NOT_HOMOLOGATED`, `BLOCKED` e `NOT_RUN` mantêm seus significados e respectivas fontes. A união de dois produtores observacionais não implementa o controlador completo V11, não demonstra eficácia financeira e não permite negociar pelo núcleo.

## Referências

Documentação primária consultada em **6 de outubro de 2026**. As afirmações sobre o candidato dependem também dos fontes, manifesto e recibos da revisão exata.

- MetaQuotes, [Expert Advisors and Custom Indicators](https://www.metatrader5.com/en/terminal/help/algotrading/trade_robots_indicators): um EA por gráfico, vários indicadores e uso analítico com negociação desabilitada.
- MetaQuotes, [Program Running](https://www.mql5.com/en/docs/runtime/running): threads, filas, ciclo de vida e limitações de Services.
- MetaQuotes, [OnTradeTransaction](https://www.mql5.com/en/docs/event_handlers/ontradetransaction): transações da conta, ordenação e reconciliação.
- MetaQuotes, [EventSetTimer](https://www.mql5.com/en/docs/eventfunctions/eventsettimer): pedido de timer e ausência de novo evento enquanto o anterior está enfileirado ou em processamento.
- MetaQuotes, [HistorySelect](https://www.mql5.com/en/docs/trading/historyselect), [HistoryDealSelect](https://www.mql5.com/en/docs/trading/historydealselect) e [HistoryOrderSelect](https://www.mql5.com/en/docs/trading/historyorderselect): listas de histórico e alterações da seleção que exigem revalidação entre etapas da preparação.
- Fontes candidatos em `mt5/jpw-alavancagem-atual/MQL5`; base preservada em `evidence/BASELINE-MANIFEST.json`; critérios em `evidence/CORE-ACCEPTANCE.json`. O manifesto final e os recibos identificam os bytes efetivamente conferidos.
