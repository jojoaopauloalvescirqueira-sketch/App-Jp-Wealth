# GENETRIX 1.19.0 — candidato de apresentação

## Identidade e limite de uso

Base: fontes completos 1.18.2, SHA-256 do ZIP `5025d6fbbed52947d3931496d23fa6c0e71f3799446a3aff6831553d8a3c2155`. Produto 1.19.0, metadado MQL 1.190 e cálculo financeiro 1.9.0. A versão interna do indicador NoCuda permanece 1.30. Consulte o manifesto para identificar os bytes, além do número de versão.

Esta revisão é `CANDIDATE`. As evidências locais e os registros de julgamento estão fora do ZIP de fontes, na entrega completa. Compilação e interação nativas precisam de evidência específica destes fontes. A existência do resumo na instalação anterior não aprova este candidato. Nenhum EX5 anterior deve ser renomeado ou apresentado como 1.19.0.

## Dois acessos no gráfico

- **Genetrix · Conta**: indicador `JPW_Alavancagem_Atual`, sete leituras e Cockpit com Visão geral, Stops, Raiz N, Sistema, Ajustes e Histórico Pessoal. Detalhes e preparação de mensagens usam rotas internas próprias.
- **NoCuda · Gráficos**: indicador `JPW_NoCuda_Channels`, estudo técnico por Fibonacci acompanhado ou desenho manual. Não oferece sinais nem envia ordens.

GENETRIX é o conjunto. Observer produz amostras de risco e Histórico Pessoal; Accountant produz o ledger dos ciclos e o flutuante compensado; Supervisor é um programa separado, com contrato de execução demo explicitamente armada. Abrir qualquer painel não inicia nem arma esses EAs. O MT5 aceita apenas um EA por gráfico; use gráficos próprios na futura validação autorizada.

## O que mudou

Apresentação e interação: identificação do módulo/seção, abas medidas pelo texto, separação entre abas e fechar, controles dimensionados pelo DPI, dois ícones próprios de ação, tratamento de área insuficiente e Tab/Shift+Tab entre ações e campos. O novo helper `JPW_UI_Design.mqh` pertence às dependências dos indicadores e desenha ícones locais em memória; os logos existentes mantêm suas proporções.

Não foram alterados fórmulas, parâmetros financeiros, formatos de armazenamento, chaves/defaults de preferências ou contratos de negociação. Preserve literalmente estados como `Current`, `Estimated`, `N/A`, `PENDING`, `BLOCKED` e `UNVERIFIED_NATIVE`. A mudança visual não homologa o modelo.

## Uso e rascunhos

Ao carregar os indicadores num ensaio isolado, confira a identidade de execução, os dois acessos e a qualidade de cada leitura. Se o gráfico for insuficiente, amplie-o; a saída deve continuar disponível. O logo pode desaparecer antes do título funcional.

Fechar o Cockpit mantém o resumo e não interrompe os EAs observadores. Tab muda o foco lógico. Enter em campo termina a edição em memória; somente uma ação explícita de botão salva/aplica quando esse botão já possui tal função. Redimensionamento e alternância de módulo não devem confirmar estudos. O foco lógico, a seleção nativa e o cursor de edição precisam de conferência real no MT5; simulação HTML não é essa evidência.

O painel usa as preferências anteriores. Não apague arquivos de preferências para obter uma captura favorável. Todas as leituras ocultas por uma escolha anterior continuam sujeitas àquela configuração; a correção não impõe visibilidade nova.

## Compilação e validação isoladas

Use um conjunto coerente: o ZIP inteiro e a biblioteca padrão identificada do MetaEditor. Compile os dois indicadores e três EAs separadamente, registre versão/build do compilador, logs, hashes dos fontes, dependências e executáveis. O retorno do processo não substitui a inspeção do log. Não distribua EX5 sem ligação comprovada aos mesmos fontes.

A suíte UI-AC01…20 congelada na entrega exige três processos locais novos e, nos percursos críticos, três sessões novas do MT5 isolado, com negociação desativada. Registre dados ausentes, erros do ambiente e falhas de produto separadamente. Protótipo, teste C++ com adaptações e compilação não aprovam por si sós a interação do terminal.

## Revisão, futura aplicação e rollback

Esta entrega não instala, não publica, não troca conta operacional e não ativa negociação. Antes de uma futura aplicação aprovada, preserve os fontes e EX5 atualmente instalados, template do gráfico, lista de indicadores/EAs, preferências e arquivos locais. Não substitua toda a pasta MQL5.

Rollback: retirar apenas os indicadores candidatos e repor o conjunto anterior coerente com suas dependências e template preservado. Restaurar preferências somente a partir do backup correto daquela instalação/conta. Não apagar nem sobrescrever Diagnostics, MDD, Stop Risk, ledger ou Histórico Pessoal. Não usar rollback para reinterpretar estados normativos ou dados financeiros.

Os manuais de versões anteriores continuam no pacote como histórico técnico. Suas declarações de teste se referem às respectivas revisões; o manifesto e os recibos desta entrega são a fonte do estado do candidato 1.19.0.
