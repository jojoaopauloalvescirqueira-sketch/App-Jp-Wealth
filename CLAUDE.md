# CLAUDE.md — entrada do Claude Code no JP Wealth

@AGENTS.md

O núcleo comum acima preserva as regras financeiras, de dados, Git, branches, worktrees, preflight, testes, preservação e aceite manual anteriormente descritas neste arquivo. A lista completa de operações Git controladas está na seção **Política Git comum** de `AGENTS.md`; não há autorização adicional neste adaptador.

Antes de editar, seguir o bootstrap comum, incluindo leitura de `README.md`, `docs/governance/CONTEXT-MAP.md`, fontes pertinentes e preflight. Conferir também instruções ancestrais/globais efetivamente fornecidas pelo ambiente; não presumir que Codex e Claude recebem a mesma cadeia. Em conflito, preservar a restrição e interromper a ação dependente, sem escolher a regra mais permissiva.

`@AGENTS.md` é a importação nativa de Claude; referências posteriores são rotas de leitura seletiva, não promessa de importação automática. Usar `/memory` e mecanismos disponíveis para verificar carregamento em sessão nova. Ausência do cliente ou de evidência fica `NOT_RUN`, nunca “compatibilidade comprovada”.

O fluxo humano está em `docs/GIT-WORKFLOW.md`; packet de delegação e limites da prova estão em `docs/governance/AI-WORKFLOW.md`. Não importar este arquivo de volta em AGENTS nem duplicar políticas para sincronizá-las manualmente.
