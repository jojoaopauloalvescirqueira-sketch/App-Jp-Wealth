# Notas — escrita sem moldura ou controles intermitentes

Pedido humano de02/11/2026: retirar Salvar/indicador intermitente e margem preta; somente revisões necessárias na mudança local. Base88f413dd74827d3c2348a70d44abcf91a2c0296e, branch existente autorizada `codex/ux-notas-menus-20261102`. N0-V/N1: somente apresentação, sem modificar escritor, debounce, persistência, backup, política de IA ou dados. Nenhuma autorização nova de commit/merge/push/publicação.

O editor permite registro e organização de Notas no JP Wealth. O defeito observado combina visibilidade do botão vinculada ao rascunho sujo e outline neutro do textarea. A superfície fica sem contorno; Salvo/Salvando ficam ocultos na apresentação normal. Falhas, resultado desconhecido, detalhes pendentes e confirmação de rascunho recuperado continuam explícitos. Botões/menus preservam foco visível; cursor, seleção e conteúdo permanecem no mesmo editor.

Arquivos permitidos: controlador Notas, CSS local, dois testes existentes, registro parcial de regressões, esta ficha e tarefa ativa; derivados somente pelo rebuild oficial. Escopo preserva todos os outros módulos e worktrees. Referências: pedido humano, renderizador `mvpNotesRecomputeDirty`/`mvpNotesAutosaveStatus`, CSS `.mvpn-content-area`; contrato anterior de autosave no CHG-UX-NOTES-MENUS, sucedido somente na apresentação normal.

Validação autorizada limitada aos focais afetados: RED real das duas regressões, GREEN nos dois artefatos; criação/digitação, foco, erro/retry, UNKNOWN, recuperação e confirmação de detalhes. Claro/escuro e320–1440px no foco, foco de botões e caret preservados. FULL anterior identifica outra versão; não será promovido para os bytes novos. FULL local/Linux novos NOT_RUN por escopo humano de revisão focal. Sem alteração de CI/gates/skill.

Reversão: reaplicar apenas o delta de apresentação a partir da cópia recuperável externa em `outputs/notes-quiet-20261102/before/`; não reverter dados nem stores. Recibos RED/GREEN, builds, hashes e capturas ficam em `outputs/notes-quiet-20261102/` da sessão Codex, fora do app. Dados sintéticos exclusivamente.
