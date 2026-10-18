# Finanças Pessoais — disponibilidade padrão congelada

- Data da solicitação: 2026-10-16.
- Status: aprovada para implementação local pelo proprietário, nesta conversa.
- Evidência humana: “quero congelar o menu de finanças pessoais”; à escolha entre projeto e navegador, “Por padrão no projeto”.
- Escopo: preferência padrão de disponibilidade; não altera norma financeira, autoridade de agentes ou direção de desenvolvimento de outros módulos.

Finanças Pessoais passa a nascer congelado, como Alladin, quando não há escolha explícita para ele. Research e Forex mantêm seus padrões. Escolhas locais válidas `personal-finance: active` ou `frozen` permanecem respeitadas; não há migração nem gravação automática para impor o novo padrão.

O menu e os acessos operacionais seguem o mecanismo central existente. Código, dados, histórico, fórmulas e formato de backup são preservados. O módulo pode ser reativado em Configurações → Editor → Módulos e disponibilidade, pelo fluxo de confirmação e releitura existente. Reativar disponibilidade não autoriza desenvolvimento ou publicação.

[Contrato técnico](../architecture/MODULE-AVAILABILITY.md). Esta decisão não declara o candidato testado, aceito ou publicado. O resultado fica no [registro de execução](../work/CHG-JPW-PF-DEFAULT-FROZEN-20261016.md). A decisão de Alladin de 2026-09-24 permanece como registro próprio.
