# Eficiência da apresentação e dos downloads

Implementação das quatro frentes autorizadas em 2026-10-14, sobre `0037bd3`, na branch `codex/app-efficiency-20261014`.

O escopo é reduzir trabalho de apresentação e distribuição. Fórmulas, escritores financeiros, formatos de backup, confirmação de gravação e resolução de rascunhos conservam os contratos existentes. As chamadas opcionais de notificação entram depois da confirmação do escritor e isolam exceções dos observadores.

## Contratos

- `render()` continua disponível. A apresentação global é atualizada e as superfícies financeiras são pintadas conforme o host efetivamente visível. Navegação aceita, abertura/fechamento de Configurações e expansão de contexto ou detalhes precisam atualizar a superfície revelada. Nós de formulários e rascunhos permanecem montados.
- O retorno de navegação para Operação pode preservar a última pintura completa válida, por certificado privado separado do snapshot da tabela. Contexto, revisões, persistência, sessão, cotações, dependências e nós montados precisam continuar equivalentes; a emissão ocorre somente após todos os pintores terminarem. Entrada inicial, render explícito, mudança, falha ou atualização parcial exigem leitura fresca.
- No Consolidado, as abas Painel, Movimentos, Estatísticas e Risco constroem somente o conteúdo da aba exposta. Gráficos e restauração de apresentação acompanham esse painel; os nós das demais abas ficam preservados até sua entrada com dados atuais.
- A grade usa um snapshot privado da última leitura fresca para prévias da linha. Instrumento, entrada, SL e TP determinam a geometria; os demais campos atualizam o rascunho. Salvar continua reconferindo o estado pelos caminhos existentes.
- `JPWNotifications.invalidate(...sourceIds)` reúne invalidações numa microtask e mantém caches separados por `system`, `forex`, `pf`, `alladin`, `calendar` e `local`. `refresh()` continua sendo síncrono e completo.
- `JPWDownloadAssets.getBytes(id, {signal})` e `getText(id, {signal})` são assíncronos. Os originais web, sidecars locais e envelopes inertes do portátil têm verificação de build, tamanho e SHA-256 antes do consumo. `JPWTools.generateEditable` passa a exigir `await`.

## Medição e regressões

`tools/app_efficiency_test.py` usa contextos descartáveis e dados sintéticos com 6, 60 e 600 ordens, além de ledger e histórico proporcionais. Instrumenta fachadas públicas sem substituir seus cálculos e exige comprovação da instalação dos contadores. Registra consultas, prévias, clones, gravações e mutações de DOM; verifica que a digitação conserva o estado confirmado e seu registro persistido.

O tempo de edição é medido do despacho do evento até dois quadros e também até uma janela de estabilização. A mediana e o p95 empírico devem ser acompanhados do número de amostras e das condições da execução. A interceptação de rede usada pelo fixture desabilita o cache HTTP: a recarga no mesmo contexto não constitui medição de PWA aquecido.

As tentativas RED e falhas intermediárias ficam preservadas em `tools/.artifacts/app-efficiency-work/`. Os testes focais de notificações, grade e downloads complementam as regressões existentes. A suíte `quality_gate.py --tier full` inclui essas verificações e as do guia interativo, da navegação, dos layouts e do zoom.

A validação final concluiu 75/75 comandos do tier full e 80/80 verificações do focal da grade/navegação. O [relatório de medição e aceite técnico](../audit/APP-EFFICIENCY-20261014.md) registra mediana, p95, contagens e limites contra a referência fixa `0037bd3`. Com 600 ordens, as medianas de edição diminuíram 85,2% no motivo e 82,5% na entrada; navegação e abertura permaneceram na escala da referência. Abertura/PWA não têm ganho demonstrado. Aceite humano, funcionamento nativo do MT5 e publicação são estados separados.
