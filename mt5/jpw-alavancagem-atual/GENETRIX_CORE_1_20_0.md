# GENETRIX 1.20.0 — Núcleo da conta

Estado: CANDIDATE. Produto 1.20.0; MQL 1.200; cálculo 1.9.0.

## Organização recomendada

- Gráfico de apoio reservado: `JPW_Genetrix_Monitor` reúne monitoramento e histórico com contabilidade de ciclos. O instrumento do gráfico não restringe a conta observada.
- Gráficos de trabalho: `JPW_Alavancagem_Atual` (Genetrix · Conta) e `JPW_NoCuda_Channels` (NoCuda · Gráficos), preservando os estudos e outros EAs.
- Supervisor 7x: opcional, separado, não requerido para as leituras. Não é instalado nem armado pela migração padrão.

Observer e Accountant legados permanecem neste pacote para rastreabilidade e rollback. Não são produtores recomendados junto ao Monitor. Encerrar os produtores antigos normalmente antes de iniciar o núcleo; nunca apagar locks ou bancos para forçar titularidade.

## Contratos preservados

Nenhum envio de ordens, fechamento ou alteração de SL/TP no núcleo. Fórmulas, agrupamento, ordenação e schemas financeiros existentes permanecem. Os inputs `InpHistoryCoverageConfirmed=false`, `InpCostCoverageConfirmed=false` e `InpCoverageEvidence=""` exigem evidência vinculada à conta original, e não são reaplicados automaticamente após troca de conta. `Partial`, `N/A`, `PENDING`, `BLOCKED` e demais estados não viram zero ou autorização financeira.

Um timer solicitado de 1s distribui tarefas com orçamento cooperativo de 500ms e preparação contábil de até 100ms por chamada. Chamadas nativas indivisíveis podem exceder o objetivo; os atrasos são medidos. Coleta, ordenação, replay e codificação são retomáveis. As listas de histórico são selecionadas novamente entre etapas; conteúdo, composição e geração-base são revalidados. A projeção e as revisões são publicadas em uma única transação; nenhuma consulta/transação principal atravessa timers.

Há três passagens de conteúdo da origem, incluindo uma após preparar a projeção. Isso detecta correções sem mudança de contagem durante a preparação. A API do MT5 não oferece snapshot transacional universal do histórico: alteração sem evento entre a última conferência e a gravação é um limite residual. Uma evidência local não demonstra ausência desse cenário em qualquer corretora.

## Diagnóstico e instalação

Genetrix · Conta → Sistema → Componentes da conta separa presença, captura, cobertura, conflito e motivo. Heartbeat não atualiza dados financeiros. Fechar o Cockpit não encerra o EA; fechar/substituir seu gráfico de apoio interrompe a coleta. Gráfico minimizado precisa de validação nativa.

Antes de instalar, preservar arquivos coerentes anteriores, perfis/modelos, preferências e bancos financeiros. Não sobrepor toda a pasta MQL5. Compilar e validar primeiro em instalação isolada, negociação desativada. Examinar logs, fontes e EX5 vinculados por hashes. Migração operacional exige a conferência visual do resumo, Cockpit e módulos funcionando juntos.

Rollback: retirar o Monitor normalmente, preservar as evidências e registros, restaurar o conjunto coerente anterior. Observer e Accountant antigos precisam de gráficos próprios. Nenhum banco financeiro é recriado ou sobrescrito automaticamente.

## Evidência

Consulte o manifesto e os recibos externos desta revisão exata. Teste local, compilação nativa, execução no terminal, instalação e aceite são estados distintos. Os 24 critérios CORE-AC01…24 foram congelados antes da implementação; todas as tentativas são preservadas. Não há aprovação operacional sem percursos nativos e conferência final.

O manual ilustrado em Markdown/PDF e a matriz de cobertura acompanham a pasta completa do candidato. Os manuais de versões anteriores descrevem seus respectivos estados históricos, não o aceite desta revisão.
